/**
 * TIERED COMMISSION & CASH WITHDRAWAL SYSTEM
 * Revolutionary commission structure:
 * - 5% base commission for everyone
 * - 10% for power users (10+ successful invites)
 * - 15% for influencers (100+ successful invites)
 * - Cash withdrawals for 100+ credits
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import Stripe from 'stripe';

class TieredCommissionWithdrawalSystem extends EventEmitter {
  constructor() {
    super();

    // Initialize services
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    this.stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

    // TIERED COMMISSION STRUCTURE
    this.commissionTiers = {
      starter: {
        name: 'Starter',
        minInvites: 0,
        maxInvites: 9,
        rate: 0.05,  // 5%
        perks: ['Basic commission', 'Monthly payouts'],
        badge: '🥉'
      },
      power: {
        name: 'Power User',
        minInvites: 10,
        maxInvites: 99,
        rate: 0.10,  // 10% - DOUBLE commission!
        perks: ['Double commission', 'Weekly payouts', 'Priority support'],
        badge: '🥈'
      },
      influencer: {
        name: 'Influencer',
        minInvites: 100,
        maxInvites: null,
        rate: 0.15,  // 15% - TRIPLE commission!
        perks: [
          'Triple commission',
          'Instant payouts',
          'Cash withdrawals',
          'Custom referral codes',
          'Dedicated account manager',
          'Early access to features'
        ],
        badge: '👑'
      },

      // Special tiers for mega influencers
      megaInfluencer: {
        name: 'Mega Influencer',
        minInvites: 500,
        rate: 0.20,  // 20% for mega influencers!
        perks: [
          '20% commission',
          'Custom landing pages',
          'API access',
          'Revenue share on renewals'
        ],
        badge: '🌟'
      }
    };

    // Cash withdrawal configuration
    this.withdrawalConfig = {
      minimumCredits: 100,        // Minimum 100 credits to withdraw
      creditToUsdRate: 0.05,      // 1 credit = $0.05
      minimumWithdrawal: 5,        // Minimum $5 withdrawal

      // Withdrawal fees
      fees: {
        percentage: 0.02,  // 2% withdrawal fee
        fixed: 0.50       // $0.50 fixed fee
      },

      // Payout methods
      methods: {
        stripe: { available: true, fee: 0 },
        paypal: { available: true, fee: 0.50 },
        crypto: { available: true, fee: 0 },
        bankTransfer: { available: true, minAmount: 100, fee: 2.50 }
      },

      // Processing times
      processingTime: {
        instant: 500,     // Instant for 500+ invites
        express: 100,     // 24 hours for 100+ invites
        standard: 10      // 3-5 days for 10+ invites
      }
    };

    // Track performance
    this.performanceStats = {
      totalCommissionsPaid: 0,
      totalCashWithdrawals: 0,
      topEarners: [],
      viralGrowthRate: 0
    };
  }

  /**
   * Calculate commission based on tier
   */
  async calculateTieredCommission(inviterId, purchaseAmount, purchaseData) {
    console.log(`💰 Calculating tiered commission for ${inviterId}`);

    try {
      // Get inviter stats
      const stats = await this.getInviterStats(inviterId);
      const tier = this.getUserTier(stats.successfulInvites);

      // Calculate base commission
      const baseCommission = purchaseAmount * tier.rate;

      // Apply bonuses
      let totalCommission = baseCommission;
      const bonuses = [];

      // First purchase bonus (extra 2%)
      if (await this.isFirstPurchase(purchaseData.userId)) {
        const firstPurchaseBonus = purchaseAmount * 0.02;
        totalCommission += firstPurchaseBonus;
        bonuses.push({
          type: 'first_purchase',
          amount: firstPurchaseBonus,
          description: 'First purchase bonus +2%'
        });
      }

      // Big spender bonus (extra 3% for purchases over $100)
      if (purchaseData.value >= 100) {
        const bigSpenderBonus = purchaseAmount * 0.03;
        totalCommission += bigSpenderBonus;
        bonuses.push({
          type: 'big_spender',
          amount: bigSpenderBonus,
          description: 'Big spender bonus +3%'
        });
      }

      // Subscription bonus (extra 5% for subscriptions)
      if (purchaseData.type === 'subscription') {
        const subscriptionBonus = purchaseAmount * 0.05;
        totalCommission += subscriptionBonus;
        bonuses.push({
          type: 'subscription',
          amount: subscriptionBonus,
          description: 'Subscription bonus +5%'
        });
      }

      // YouTube/Influencer special bonus
      if (stats.isVerifiedInfluencer) {
        const influencerBonus = purchaseAmount * 0.05;
        totalCommission += influencerBonus;
        bonuses.push({
          type: 'verified_influencer',
          amount: influencerBonus,
          description: 'Verified influencer bonus +5%'
        });
      }

      return {
        inviterId,
        tier: tier.name,
        baseRate: tier.rate,
        baseCommission: Math.floor(baseCommission),
        bonuses,
        totalCommission: Math.floor(totalCommission),
        effectiveRate: totalCommission / purchaseAmount,
        badge: tier.badge
      };

    } catch (error) {
      console.error('Failed to calculate commission:', error);
      throw error;
    }
  }

  /**
   * Get user tier based on successful invites
   */
  getUserTier(successfulInvites) {
    if (successfulInvites >= 500) return this.commissionTiers.megaInfluencer;
    if (successfulInvites >= 100) return this.commissionTiers.influencer;
    if (successfulInvites >= 10) return this.commissionTiers.power;
    return this.commissionTiers.starter;
  }

  /**
   * Process cash withdrawal
   */
  async processCashWithdrawal(userId, withdrawalRequest) {
    console.log(`💸 Processing cash withdrawal for ${userId}`);

    const {
      credits,
      method,
      destination  // PayPal email, crypto address, bank account, etc.
    } = withdrawalRequest;

    try {
      // Validate withdrawal
      const validation = await this.validateWithdrawal(userId, credits, method);

      if (!validation.valid) {
        return {
          success: false,
          error: validation.error,
          suggestion: validation.suggestion
        };
      }

      // Calculate withdrawal amount
      const withdrawal = this.calculateWithdrawalAmount(credits, method);

      // Check user balance
      const userBalance = await this.getUserCreditBalance(userId);
      if (userBalance < credits) {
        return {
          success: false,
          error: 'Insufficient credits',
          balance: userBalance,
          required: credits
        };
      }

      // Process based on method
      let payoutResult;

      switch (method) {
        case 'stripe':
          payoutResult = await this.processStripePayout(userId, withdrawal, destination);
          break;

        case 'paypal':
          payoutResult = await this.processPayPalPayout(userId, withdrawal, destination);
          break;

        case 'crypto':
          payoutResult = await this.processCryptoPayout(userId, withdrawal, destination);
          break;

        case 'bankTransfer':
          payoutResult = await this.processBankTransfer(userId, withdrawal, destination);
          break;

        default:
          throw new Error('Invalid withdrawal method');
      }

      // Deduct credits from user account
      await this.deductCredits(userId, credits);

      // Record withdrawal
      await this.recordWithdrawal(userId, {
        credits,
        method,
        amount: withdrawal.netAmount,
        fee: withdrawal.totalFee,
        destination,
        status: 'completed',
        transactionId: payoutResult.transactionId,
        timestamp: new Date().toISOString()
      });

      // Send confirmation
      await this.sendWithdrawalConfirmation(userId, withdrawal, payoutResult);

      return {
        success: true,
        withdrawal: {
          credits: credits,
          grossAmount: withdrawal.grossAmount,
          fee: withdrawal.totalFee,
          netAmount: withdrawal.netAmount,
          method: method,
          transactionId: payoutResult.transactionId,
          processingTime: this.getProcessingTime(userId, method),
          status: 'completed'
        },
        remainingBalance: userBalance - credits
      };

    } catch (error) {
      console.error('Withdrawal failed:', error);

      // Record failed withdrawal
      await this.recordWithdrawal(userId, {
        credits,
        method,
        status: 'failed',
        error: error.message,
        timestamp: new Date().toISOString()
      });

      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Calculate withdrawal amount after fees
   */
  calculateWithdrawalAmount(credits, method) {
    const grossAmount = credits * this.withdrawalConfig.creditToUsdRate;

    // Calculate fees
    const percentageFee = grossAmount * this.withdrawalConfig.fees.percentage;
    const fixedFee = this.withdrawalConfig.fees.fixed;
    const methodFee = this.withdrawalConfig.methods[method]?.fee || 0;

    const totalFee = percentageFee + fixedFee + methodFee;
    const netAmount = grossAmount - totalFee;

    return {
      credits,
      grossAmount: grossAmount.toFixed(2),
      percentageFee: percentageFee.toFixed(2),
      fixedFee: fixedFee.toFixed(2),
      methodFee: methodFee.toFixed(2),
      totalFee: totalFee.toFixed(2),
      netAmount: netAmount.toFixed(2),
      exchangeRate: this.withdrawalConfig.creditToUsdRate
    };
  }

  /**
   * Validate withdrawal request
   */
  async validateWithdrawal(userId, credits, method) {
    // Check minimum credits
    if (credits < this.withdrawalConfig.minimumCredits) {
      return {
        valid: false,
        error: `Minimum withdrawal is ${this.withdrawalConfig.minimumCredits} credits`,
        suggestion: `Earn ${this.withdrawalConfig.minimumCredits - credits} more credits`
      };
    }

    // Check minimum USD amount
    const usdAmount = credits * this.withdrawalConfig.creditToUsdRate;
    if (usdAmount < this.withdrawalConfig.minimumWithdrawal) {
      return {
        valid: false,
        error: `Minimum withdrawal is $${this.withdrawalConfig.minimumWithdrawal}`,
        suggestion: `Need ${Math.ceil((this.withdrawalConfig.minimumWithdrawal - usdAmount) / this.withdrawalConfig.creditToUsdRate)} more credits`
      };
    }

    // Check if method is available
    if (!this.withdrawalConfig.methods[method]?.available) {
      return {
        valid: false,
        error: 'Withdrawal method not available',
        suggestion: 'Choose a different method'
      };
    }

    // Check method-specific requirements
    if (method === 'bankTransfer' && usdAmount < this.withdrawalConfig.methods.bankTransfer.minAmount) {
      return {
        valid: false,
        error: `Bank transfer minimum is $${this.withdrawalConfig.methods.bankTransfer.minAmount}`,
        suggestion: 'Use PayPal or crypto for smaller amounts'
      };
    }

    // Check user verification status for large withdrawals
    if (usdAmount > 500) {
      const isVerified = await this.isUserVerified(userId);
      if (!isVerified) {
        return {
          valid: false,
          error: 'Verification required for withdrawals over $500',
          suggestion: 'Complete identity verification in settings'
        };
      }
    }

    return { valid: true };
  }

  /**
   * Get influencer dashboard data
   */
  async getInfluencerDashboard(userId) {
    const stats = await this.getInviterStats(userId);
    const tier = this.getUserTier(stats.successfulInvites);

    return {
      // Current tier info
      currentTier: {
        name: tier.name,
        rate: `${tier.rate * 100}%`,
        badge: tier.badge,
        perks: tier.perks
      },

      // Progress to next tier
      nextTier: this.getNextTier(stats.successfulInvites),

      // Earnings
      earnings: {
        today: await this.getTodayEarnings(userId),
        thisWeek: await this.getWeekEarnings(userId),
        thisMonth: await this.getMonthEarnings(userId),
        total: await this.getTotalEarnings(userId),
        available: await this.getAvailableBalance(userId),
        pending: await this.getPendingCommissions(userId)
      },

      // Network stats
      network: {
        totalInvites: stats.totalInvitesSent,
        successfulInvites: stats.successfulInvites,
        conversionRate: `${((stats.successfulInvites / stats.totalInvitesSent) * 100).toFixed(1)}%`,
        activeUsers: await this.getActiveNetworkUsers(userId),
        totalNetworkSpend: await this.getTotalNetworkSpend(userId)
      },

      // Withdrawal options
      withdrawal: {
        available: stats.availableBalance >= this.withdrawalConfig.minimumCredits,
        minimumCredits: this.withdrawalConfig.minimumCredits,
        exchangeRate: this.withdrawalConfig.creditToUsdRate,
        methods: Object.keys(this.withdrawalConfig.methods).filter(m =>
          this.withdrawalConfig.methods[m].available
        ),
        estimatedPayout: this.calculateWithdrawalAmount(stats.availableBalance, 'stripe')
      },

      // Performance metrics
      performance: {
        rank: await this.getInfluencerRank(userId),
        percentile: await this.getPercentile(userId),
        growthRate: await this.getGrowthRate(userId),
        projectedEarnings: await this.projectEarnings(userId)
      },

      // Custom tools for influencers
      tools: tier.name === 'Influencer' ? {
        customLink: await this.getCustomReferralLink(userId),
        promoMaterials: await this.getPromoMaterials(userId),
        analytics: await this.getDetailedAnalytics(userId),
        apiAccess: stats.successfulInvites >= 500
      } : null
    };
  }

  /**
   * Get next tier information
   */
  getNextTier(currentInvites) {
    if (currentInvites < 10) {
      return {
        name: this.commissionTiers.power.name,
        rate: `${this.commissionTiers.power.rate * 100}%`,
        invitesNeeded: 10 - currentInvites,
        perks: this.commissionTiers.power.perks,
        message: `Get ${10 - currentInvites} more invites to DOUBLE your commission!`
      };
    }

    if (currentInvites < 100) {
      return {
        name: this.commissionTiers.influencer.name,
        rate: `${this.commissionTiers.influencer.rate * 100}%`,
        invitesNeeded: 100 - currentInvites,
        perks: this.commissionTiers.influencer.perks,
        message: `Get ${100 - currentInvites} more invites to TRIPLE your commission & unlock cash withdrawals!`
      };
    }

    if (currentInvites < 500) {
      return {
        name: this.commissionTiers.megaInfluencer.name,
        rate: `${this.commissionTiers.megaInfluencer.rate * 100}%`,
        invitesNeeded: 500 - currentInvites,
        perks: this.commissionTiers.megaInfluencer.perks,
        message: `Get ${500 - currentInvites} more invites for 20% commission & mega influencer status!`
      };
    }

    return {
      name: 'Maximum',
      message: `You've reached the highest tier! Keep growing your network for unlimited earnings!`
    };
  }

  /**
   * Generate custom referral materials for influencers
   */
  async generateInfluencerMaterials(userId) {
    const stats = await this.getInviterStats(userId);

    if (stats.successfulInvites < 100) {
      return {
        available: false,
        message: 'Reach 100 invites to unlock custom materials'
      };
    }

    return {
      available: true,
      materials: {
        // Custom landing page
        landingPage: {
          url: `https://zmarty.ai/${stats.username}`,
          customizable: true,
          analytics: true
        },

        // Promotional content
        content: {
          tweets: await this.generateTweetTemplates(userId),
          youtube: await this.generateYouTubeDescription(userId),
          discord: await this.generateDiscordAnnouncement(userId),
          email: await this.generateEmailTemplate(userId)
        },

        // Visual assets
        assets: {
          banners: ['728x90', '300x250', '160x600'],
          badges: ['influencer', 'top_earner', 'verified'],
          charts: ['earnings', 'growth', 'success_rate']
        },

        // Tracking
        tracking: {
          customCodes: await this.generateCustomCodes(userId, 10),
          utmBuilder: true,
          realTimeStats: true
        }
      }
    };
  }

  /**
   * Project future earnings for influencer
   */
  async projectEarnings(userId) {
    const stats = await this.getInviterStats(userId);
    const tier = this.getUserTier(stats.successfulInvites);
    const networkGrowth = await this.calculateNetworkGrowth(userId);

    // Base projections on current performance
    const avgPurchasePerUser = 500; // 500 credits average
    const monthlyPurchases = 2; // 2 purchases per user per month

    const projections = {
      nextMonth: Math.floor(
        stats.activeNetworkUsers * avgPurchasePerUser * monthlyPurchases * tier.rate
      ),
      next3Months: Math.floor(
        stats.activeNetworkUsers * avgPurchasePerUser * monthlyPurchases * 3 * tier.rate * networkGrowth
      ),
      next6Months: Math.floor(
        stats.activeNetworkUsers * avgPurchasePerUser * monthlyPurchases * 6 * tier.rate * Math.pow(networkGrowth, 2)
      ),
      nextYear: Math.floor(
        stats.activeNetworkUsers * avgPurchasePerUser * monthlyPurchases * 12 * tier.rate * Math.pow(networkGrowth, 4)
      ),

      // Cash projections
      cashNextMonth: null,
      cashNextYear: null
    };

    // Calculate cash amounts
    projections.cashNextMonth = (projections.nextMonth * this.withdrawalConfig.creditToUsdRate).toFixed(2);
    projections.cashNextYear = (projections.nextYear * this.withdrawalConfig.creditToUsdRate).toFixed(2);

    return projections;
  }
}

// Export singleton
const commissionSystem = new TieredCommissionWithdrawalSystem();
export default commissionSystem;