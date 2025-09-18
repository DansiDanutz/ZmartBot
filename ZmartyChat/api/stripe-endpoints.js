// Stripe Backend API Endpoints for ZmartyChat
import Stripe from 'stripe';
import express from 'express';
import { zmartyDB } from '../src/supabase-client.js';

// Initialize Stripe with secret key
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || 'sk_test_your_key_here');
const router = express.Router();

// Webhook secret for verifying Stripe events
const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET || 'whsec_your_secret_here';

// ============= PAYMENT INTENT ENDPOINTS =============

router.post('/create-payment-intent', async (req, res) => {
    const { packageId, userId, amount, credits, bonus } = req.body;

    try {
        // Create payment intent
        const paymentIntent = await stripe.paymentIntents.create({
            amount: amount, // Amount in cents
            currency: 'usd',
            automatic_payment_methods: {
                enabled: true,
            },
            metadata: {
                userId,
                packageId,
                credits: credits.toString(),
                bonus: bonus.toString()
            }
        });

        res.json({
            clientSecret: paymentIntent.client_secret
        });
    } catch (error) {
        console.error('Payment Intent Error:', error);
        res.status(400).json({ error: error.message });
    }
});

router.post('/confirm-payment', async (req, res) => {
    const { paymentIntentId, userId, packageId } = req.body;

    try {
        // Retrieve payment intent to verify it's successful
        const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId);

        if (paymentIntent.status !== 'succeeded') {
            throw new Error('Payment not successful');
        }

        // Add credits to user account
        const totalCredits = parseInt(paymentIntent.metadata.credits) +
                           parseInt(paymentIntent.metadata.bonus || 0);

        await zmartyDB.addCredits(
            userId,
            totalCredits,
            'purchase',
            `Package purchase: ${packageId}`,
            {
                method: 'stripe',
                id: paymentIntentId,
                currency: 'USD',
                amountPaid: paymentIntent.amount / 100
            }
        );

        res.json({ success: true, credits: totalCredits });
    } catch (error) {
        console.error('Payment Confirmation Error:', error);
        res.status(400).json({ error: error.message });
    }
});

// ============= SUBSCRIPTION ENDPOINTS =============

router.post('/create-subscription', async (req, res) => {
    const { planId, userId, paymentMethodId } = req.body;

    try {
        // First create or get customer
        let customer;
        const user = await zmartyDB.getUser(userId);

        if (user.stripe_customer_id) {
            customer = await stripe.customers.retrieve(user.stripe_customer_id);
        } else {
            customer = await stripe.customers.create({
                email: user.email,
                metadata: {
                    userId: userId
                }
            });

            // Save customer ID to database
            await zmartyDB.updateUser(userId, {
                stripe_customer_id: customer.id
            });
        }

        // Attach payment method to customer
        await stripe.paymentMethods.attach(paymentMethodId, {
            customer: customer.id,
        });

        // Set as default payment method
        await stripe.customers.update(customer.id, {
            invoice_settings: {
                default_payment_method: paymentMethodId,
            },
        });

        // Get price ID based on plan
        const priceIds = {
            basic: process.env.STRIPE_PRICE_BASIC || 'price_basic',
            pro: process.env.STRIPE_PRICE_PRO || 'price_pro',
            premium: process.env.STRIPE_PRICE_PREMIUM || 'price_premium'
        };

        // Create subscription
        const subscription = await stripe.subscriptions.create({
            customer: customer.id,
            items: [{ price: priceIds[planId] }],
            payment_settings: {
                payment_method_types: ['card'],
                save_default_payment_method: 'on_subscription'
            },
            expand: ['latest_invoice.payment_intent'],
            metadata: {
                userId: userId,
                planId: planId
            }
        });

        res.json(subscription);
    } catch (error) {
        console.error('Subscription Creation Error:', error);
        res.status(400).json({ error: error.message });
    }
});

router.post('/cancel-subscription', async (req, res) => {
    const { subscriptionId } = req.body;

    try {
        // Cancel at period end to give user remaining time
        const subscription = await stripe.subscriptions.update(subscriptionId, {
            cancel_at_period_end: true
        });

        res.json({ success: true, subscription });
    } catch (error) {
        console.error('Subscription Cancellation Error:', error);
        res.status(400).json({ error: error.message });
    }
});

router.post('/update-payment-method', async (req, res) => {
    const { subscriptionId, paymentMethodId } = req.body;

    try {
        const subscription = await stripe.subscriptions.retrieve(subscriptionId);

        // Attach new payment method to customer
        await stripe.paymentMethods.attach(paymentMethodId, {
            customer: subscription.customer,
        });

        // Update customer's default payment method
        await stripe.customers.update(subscription.customer, {
            invoice_settings: {
                default_payment_method: paymentMethodId,
            },
        });

        res.json({ success: true });
    } catch (error) {
        console.error('Payment Method Update Error:', error);
        res.status(400).json({ error: error.message });
    }
});

// ============= PAYMENT METHOD ENDPOINTS =============

router.post('/save-payment-method', async (req, res) => {
    const { paymentMethodId, userId } = req.body;

    try {
        const user = await zmartyDB.getUser(userId);

        if (!user.stripe_customer_id) {
            throw new Error('Customer not found');
        }

        // Attach payment method to customer
        await stripe.paymentMethods.attach(paymentMethodId, {
            customer: user.stripe_customer_id,
        });

        // List all payment methods to return
        const paymentMethods = await stripe.paymentMethods.list({
            customer: user.stripe_customer_id,
            type: 'card',
        });

        res.json({ success: true, paymentMethods: paymentMethods.data });
    } catch (error) {
        console.error('Save Payment Method Error:', error);
        res.status(400).json({ error: error.message });
    }
});

router.delete('/payment-method/:methodId', async (req, res) => {
    const { methodId } = req.params;

    try {
        await stripe.paymentMethods.detach(methodId);
        res.json({ success: true });
    } catch (error) {
        console.error('Delete Payment Method Error:', error);
        res.status(400).json({ error: error.message });
    }
});

// ============= WEBHOOK ENDPOINT =============

router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    let event;

    try {
        event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
        console.error('Webhook Error:', err.message);
        return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    try {
        switch (event.type) {
            case 'payment_intent.succeeded':
                await handlePaymentIntentSucceeded(event.data.object);
                break;

            case 'payment_intent.payment_failed':
                await handlePaymentIntentFailed(event.data.object);
                break;

            case 'customer.subscription.created':
            case 'customer.subscription.updated':
                await handleSubscriptionChange(event.data.object);
                break;

            case 'customer.subscription.deleted':
                await handleSubscriptionDeleted(event.data.object);
                break;

            case 'invoice.paid':
                await handleInvoicePaid(event.data.object);
                break;

            case 'invoice.payment_failed':
                await handleInvoicePaymentFailed(event.data.object);
                break;

            default:
                console.log(`Unhandled event type: ${event.type}`);
        }

        res.json({ received: true });
    } catch (error) {
        console.error('Webhook Processing Error:', error);
        res.status(500).json({ error: error.message });
    }
});

// ============= WEBHOOK HANDLERS =============

async function handlePaymentIntentSucceeded(paymentIntent) {
    const { userId, credits, bonus, packageId } = paymentIntent.metadata;

    if (userId && credits) {
        const totalCredits = parseInt(credits) + parseInt(bonus || 0);

        await zmartyDB.addCredits(
            userId,
            totalCredits,
            'purchase',
            `Credit package purchased: ${packageId}`,
            {
                method: 'stripe',
                id: paymentIntent.id,
                currency: paymentIntent.currency.toUpperCase(),
                amountPaid: paymentIntent.amount / 100
            }
        );

        console.log(`Added ${totalCredits} credits to user ${userId}`);
    }
}

async function handlePaymentIntentFailed(paymentIntent) {
    const { userId } = paymentIntent.metadata;

    console.error(`Payment failed for user ${userId}:`, paymentIntent.last_payment_error);

    // Could send notification to user about failed payment
}

async function handleSubscriptionChange(subscription) {
    const { userId, planId } = subscription.metadata;

    const planCredits = {
        basic: 1000,
        pro: 5000,
        premium: 20000
    };

    await zmartyDB.createSubscription(userId, planId, {
        method: 'stripe',
        stripeId: subscription.id
    });

    // Add initial subscription credits if it's a new subscription
    if (subscription.status === 'active' && subscription.created === subscription.current_period_start) {
        await zmartyDB.addCredits(
            userId,
            planCredits[planId],
            'subscription',
            `${planId} plan activated`,
            {
                method: 'stripe',
                id: subscription.id
            }
        );
    }

    console.log(`Subscription ${subscription.id} updated for user ${userId}`);
}

async function handleSubscriptionDeleted(subscription) {
    const { userId } = subscription.metadata;

    // Update user's subscription status
    await zmartyDB.updateUser(userId, {
        subscription_tier: 'free',
        subscription_status: 'cancelled'
    });

    console.log(`Subscription cancelled for user ${userId}`);
}

async function handleInvoicePaid(invoice) {
    // Add monthly credits for subscription renewal
    if (invoice.billing_reason === 'subscription_cycle') {
        const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
        const { userId, planId } = subscription.metadata;

        const planCredits = {
            basic: 1000,
            pro: 5000,
            premium: 20000
        };

        await zmartyDB.addCredits(
            userId,
            planCredits[planId],
            'subscription',
            'Monthly subscription renewal',
            {
                method: 'stripe',
                id: invoice.id,
                currency: invoice.currency.toUpperCase(),
                amountPaid: invoice.amount_paid / 100
            }
        );

        console.log(`Monthly credits added for user ${userId}`);
    }
}

async function handleInvoicePaymentFailed(invoice) {
    const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
    const { userId } = subscription.metadata;

    console.error(`Invoice payment failed for user ${userId}`);

    // Could send notification or suspend account
}

// ============= BILLING HISTORY ENDPOINTS =============

router.get('/payment-history/:userId', async (req, res) => {
    const { userId } = req.params;

    try {
        const user = await zmartyDB.getUser(userId);

        if (!user.stripe_customer_id) {
            return res.json({ payments: [] });
        }

        // Get charges
        const charges = await stripe.charges.list({
            customer: user.stripe_customer_id,
            limit: 100
        });

        // Get invoices
        const invoices = await stripe.invoices.list({
            customer: user.stripe_customer_id,
            limit: 100
        });

        res.json({
            charges: charges.data,
            invoices: invoices.data
        });
    } catch (error) {
        console.error('Payment History Error:', error);
        res.status(400).json({ error: error.message });
    }
});

router.get('/invoice/:invoiceId', async (req, res) => {
    const { invoiceId } = req.params;

    try {
        const invoice = await stripe.invoices.retrieve(invoiceId);

        if (!invoice.invoice_pdf) {
            throw new Error('Invoice PDF not available');
        }

        // Redirect to Stripe's hosted invoice PDF
        res.redirect(invoice.invoice_pdf);
    } catch (error) {
        console.error('Invoice Download Error:', error);
        res.status(400).json({ error: error.message });
    }
});

// ============= CUSTOMER PORTAL =============

router.post('/create-portal-session', async (req, res) => {
    const { userId } = req.body;

    try {
        const user = await zmartyDB.getUser(userId);

        if (!user.stripe_customer_id) {
            throw new Error('No billing account found');
        }

        const session = await stripe.billingPortal.sessions.create({
            customer: user.stripe_customer_id,
            return_url: `${process.env.FRONTEND_URL}/settings/billing`
        });

        res.json({ url: session.url });
    } catch (error) {
        console.error('Portal Session Error:', error);
        res.status(400).json({ error: error.message });
    }
});

export default router;