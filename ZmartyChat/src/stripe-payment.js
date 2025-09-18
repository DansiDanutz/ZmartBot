// Stripe Payment Integration for ZmartyChat
import { loadStripe } from '@stripe/stripe-js';
import { zmartyDB } from './supabase-client.js';
import { creditManager } from './credit-manager.js';

// Initialize Stripe
const stripePromise = loadStripe(process.env.STRIPE_PUBLISHABLE_KEY || 'pk_test_your_key_here');

export class StripePaymentProcessor {
    constructor() {
        this.stripe = null;
        this.elements = null;
        this.currentPaymentIntent = null;
        this.webhookEndpoint = process.env.STRIPE_WEBHOOK_ENDPOINT || '/api/stripe/webhook';

        this.init();
    }

    async init() {
        this.stripe = await stripePromise;
    }

    // ============= ONE-TIME CREDIT PURCHASES =============

    async createPaymentIntent(packageId, userId) {
        const creditPackage = creditManager.packages[packageId];

        if (!creditPackage) {
            throw new Error('Invalid package selected');
        }

        try {
            // Call backend to create payment intent
            const response = await fetch('/api/stripe/create-payment-intent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                },
                body: JSON.stringify({
                    packageId,
                    userId,
                    amount: creditPackage.price * 100, // Convert to cents
                    credits: creditPackage.credits,
                    bonus: creditPackage.bonus || 0
                })
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.currentPaymentIntent = data.clientSecret;
            return data.clientSecret;
        } catch (error) {
            console.error('Payment Intent Creation Error:', error);
            throw error;
        }
    }

    async mountCardElement(elementId) {
        if (!this.stripe) {
            await this.init();
        }

        this.elements = this.stripe.elements();

        const cardElement = this.elements.create('card', {
            style: {
                base: {
                    fontSize: '16px',
                    color: '#424770',
                    '::placeholder': {
                        color: '#aab7c4',
                    },
                },
                invalid: {
                    color: '#9e2146',
                },
            },
            hidePostalCode: false
        });

        cardElement.mount(`#${elementId}`);
        return cardElement;
    }

    async processPayment(cardElement, billingDetails) {
        if (!this.stripe || !this.currentPaymentIntent) {
            throw new Error('Payment not initialized');
        }

        const { error, paymentIntent } = await this.stripe.confirmCardPayment(
            this.currentPaymentIntent,
            {
                payment_method: {
                    card: cardElement,
                    billing_details: billingDetails
                }
            }
        );

        if (error) {
            throw error;
        }

        return paymentIntent;
    }

    async completePurchase(paymentIntent, userId, packageId) {
        const creditPackage = creditManager.packages[packageId];
        const totalCredits = creditPackage.credits + (creditPackage.bonus || 0);

        // Record transaction in database
        const transaction = await zmartyDB.addCredits(
            userId,
            totalCredits,
            'purchase',
            `Purchased ${creditPackage.name} package`,
            {
                method: 'stripe',
                id: paymentIntent.id,
                currency: 'USD',
                amountPaid: creditPackage.price
            }
        );

        // Trigger success animation
        this.showPurchaseSuccess(totalCredits);

        return transaction;
    }

    // ============= SUBSCRIPTION MANAGEMENT =============

    async createSubscription(planId, userId, paymentMethodId) {
        try {
            const response = await fetch('/api/stripe/create-subscription', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                },
                body: JSON.stringify({
                    planId,
                    userId,
                    paymentMethodId
                })
            });

            const subscription = await response.json();

            if (subscription.error) {
                throw new Error(subscription.error);
            }

            // Update user's subscription in database
            await zmartyDB.createSubscription(
                userId,
                planId,
                {
                    method: 'stripe',
                    stripeId: subscription.id
                }
            );

            return subscription;
        } catch (error) {
            console.error('Subscription Creation Error:', error);
            throw error;
        }
    }

    async cancelSubscription(subscriptionId) {
        try {
            const response = await fetch('/api/stripe/cancel-subscription', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                },
                body: JSON.stringify({ subscriptionId })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Subscription Cancellation Error:', error);
            throw error;
        }
    }

    async updatePaymentMethod(subscriptionId, newPaymentMethodId) {
        try {
            const response = await fetch('/api/stripe/update-payment-method', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                },
                body: JSON.stringify({
                    subscriptionId,
                    paymentMethodId: newPaymentMethodId
                })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Payment Method Update Error:', error);
            throw error;
        }
    }

    // ============= PAYMENT UI COMPONENTS =============

    renderCreditPackages() {
        const packagesContainer = document.createElement('div');
        packagesContainer.className = 'credit-packages-grid';

        Object.entries(creditManager.packages).forEach(([id, creditPackage]) => {
            const packageCard = document.createElement('div');
            packageCard.className = 'package-card';

            if (creditPackage.popular) {
                packageCard.classList.add('popular');
            }

            packageCard.innerHTML = `
                <div class="package-header">
                    ${creditPackage.popular ? '<div class="popular-badge">MOST POPULAR</div>' : ''}
                    <h3>${creditPackage.name}</h3>
                </div>
                <div class="package-credits">
                    <span class="credits-amount">${creditPackage.credits.toLocaleString()}</span>
                    <span class="credits-label">Credits</span>
                    ${creditPackage.bonus ? `<div class="bonus">+${creditPackage.bonus} bonus!</div>` : ''}
                </div>
                <div class="package-price">
                    <span class="currency">$</span>
                    <span class="amount">${creditPackage.price}</span>
                </div>
                <div class="package-value">
                    $${(creditPackage.price / creditPackage.credits * 1000).toFixed(2)} per 1000 credits
                </div>
                <button class="buy-button" data-package="${id}">
                    Buy Now
                </button>
            `;

            packagesContainer.appendChild(packageCard);
        });

        return packagesContainer;
    }

    renderSubscriptionPlans() {
        const plansContainer = document.createElement('div');
        plansContainer.className = 'subscription-plans';

        const plans = [
            {
                id: 'basic',
                name: 'Basic',
                price: 9.99,
                credits: 1000,
                features: [
                    '1,000 credits/month',
                    'Basic AI analysis',
                    'Email support'
                ]
            },
            {
                id: 'pro',
                name: 'Pro',
                price: 29.99,
                credits: 5000,
                popular: true,
                features: [
                    '5,000 credits/month',
                    'Advanced AI features',
                    'Priority support',
                    'Custom alerts'
                ]
            },
            {
                id: 'premium',
                name: 'Premium',
                price: 99.99,
                credits: 20000,
                features: [
                    '20,000 credits/month',
                    'All AI features',
                    'White-glove support',
                    'API access',
                    'Custom models'
                ]
            }
        ];

        plans.forEach(plan => {
            const planCard = document.createElement('div');
            planCard.className = 'plan-card';

            if (plan.popular) {
                planCard.classList.add('popular');
            }

            planCard.innerHTML = `
                <div class="plan-header">
                    ${plan.popular ? '<div class="popular-badge">RECOMMENDED</div>' : ''}
                    <h3>${plan.name}</h3>
                    <div class="plan-price">
                        <span class="currency">$</span>
                        <span class="amount">${plan.price}</span>
                        <span class="period">/month</span>
                    </div>
                </div>
                <div class="plan-features">
                    ${plan.features.map(f => `<div class="feature">✓ ${f}</div>`).join('')}
                </div>
                <button class="subscribe-button" data-plan="${plan.id}">
                    Subscribe
                </button>
            `;

            plansContainer.appendChild(planCard);
        });

        return plansContainer;
    }

    showPurchaseSuccess(credits) {
        const successModal = document.createElement('div');
        successModal.className = 'payment-success-modal';

        successModal.innerHTML = `
            <div class="success-content">
                <div class="success-icon">🎉</div>
                <h2>Payment Successful!</h2>
                <p>${credits.toLocaleString()} credits have been added to your account</p>
                <button class="continue-button">Continue Trading</button>
            </div>
        `;

        document.body.appendChild(successModal);

        // Trigger confetti animation
        this.triggerConfetti();

        // Remove modal after animation
        setTimeout(() => {
            successModal.remove();
        }, 3000);
    }

    triggerConfetti() {
        // Simple confetti animation
        const colors = ['#FF6B35', '#00D084', '#FFD700', '#FF69B4'];
        const confettiCount = 100;

        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.animationDelay = Math.random() * 3 + 's';
            confetti.style.animationDuration = Math.random() * 3 + 2 + 's';

            document.body.appendChild(confetti);

            setTimeout(() => confetti.remove(), 5000);
        }
    }

    // ============= PAYMENT SECURITY =============

    async validate3DSecure(paymentIntentId) {
        const { error, paymentIntent } = await this.stripe.handleCardAction(paymentIntentId);

        if (error) {
            throw error;
        }

        return paymentIntent;
    }

    async savePaymentMethod(paymentMethodId, userId) {
        try {
            const response = await fetch('/api/stripe/save-payment-method', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                },
                body: JSON.stringify({
                    paymentMethodId,
                    userId
                })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Save Payment Method Error:', error);
            throw error;
        }
    }

    // ============= WEBHOOK HANDLERS =============

    async handleWebhook(event) {
        switch (event.type) {
            case 'payment_intent.succeeded':
                await this.handleSuccessfulPayment(event.data.object);
                break;

            case 'payment_intent.payment_failed':
                await this.handleFailedPayment(event.data.object);
                break;

            case 'customer.subscription.created':
            case 'customer.subscription.updated':
                await this.handleSubscriptionUpdate(event.data.object);
                break;

            case 'customer.subscription.deleted':
                await this.handleSubscriptionCancellation(event.data.object);
                break;

            case 'invoice.payment_succeeded':
                await this.handleInvoicePayment(event.data.object);
                break;

            default:
                console.log(`Unhandled webhook event: ${event.type}`);
        }
    }

    async handleSuccessfulPayment(paymentIntent) {
        const metadata = paymentIntent.metadata;

        await zmartyDB.addCredits(
            metadata.userId,
            parseInt(metadata.credits),
            'purchase',
            `Payment completed: ${paymentIntent.id}`
        );
    }

    async handleFailedPayment(paymentIntent) {
        console.error('Payment failed:', paymentIntent.id);
        // Notify user of failed payment
    }

    async handleSubscriptionUpdate(subscription) {
        // Update subscription status in database
        console.log('Subscription updated:', subscription.id);
    }

    async handleSubscriptionCancellation(subscription) {
        // Handle subscription cancellation
        console.log('Subscription cancelled:', subscription.id);
    }

    async handleInvoicePayment(invoice) {
        // Add monthly subscription credits
        const metadata = invoice.metadata;

        if (metadata.monthlyCredits) {
            await zmartyDB.addCredits(
                metadata.userId,
                parseInt(metadata.monthlyCredits),
                'subscription',
                'Monthly subscription renewal'
            );
        }
    }

    // ============= PAYMENT HISTORY =============

    async getPaymentHistory(userId) {
        try {
            const response = await fetch(`/api/stripe/payment-history/${userId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                }
            });

            const history = await response.json();
            return history;
        } catch (error) {
            console.error('Payment History Error:', error);
            throw error;
        }
    }

    async downloadInvoice(invoiceId) {
        try {
            const response = await fetch(`/api/stripe/invoice/${invoiceId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt')}`
                }
            });

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `invoice-${invoiceId}.pdf`;
            a.click();

            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Invoice Download Error:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const stripePayment = new StripePaymentProcessor();

// Auto-initialize on page load
if (typeof window !== 'undefined') {
    window.stripePayment = stripePayment;
}