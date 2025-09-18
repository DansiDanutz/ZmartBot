/**
 * VIRAL REVENUE SHARE SYSTEM
 * The rocket fuel for explosive growth:
 * - Inviters get 5% of ALL credit purchases from their invites FOREVER
 * - Creates passive income for early adopters
 * - Motivates aggressive invitation spreading
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import ExclusiveInvitationSystem from './ExclusiveInvitationSystem.js';

class ViralRevenueShareSystem extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Revenue share configuration
    this.config = {
      // Commission structure
      commissions: {
        direct: 0.05,           // 5% to direct inviter
        secondTier: 0.02,       // 2% to inviter's inviter (MLM style)
        thirdTier: 0.01,        // 1% to third tier (for whales)

        // Bonus multipliers for top inviters
        multipliers: {
          bronze: 1.0,      // 1-5 invites: standard 5%
          silver: 1.2,      // 5-10 invites: 6%
          gold: 1.5,        // 10-25 invites: 7.5%
          diamond: 2.0,     // 25-50 invites: 10%
          whale: 2.5,       // 50-100 invites: 12.5%
          legend: 3.0       // 100+ invites: 15%
        }
      },

      // Passive income tiers
      passiveIncome: {
        minimumForPayout: 100,      // Minimum 100 credits for payout
        payoutFrequency: 'weekly',  // Weekly payouts
        instantPayout: 1000        // Instant payout for 1000+ credits
      },

      // Growth incentives
      bonuses: {
        firstPurchaseBonus: 50,     // Extra 50 credits when invite makes first purchase
        bigSpenderBonus: 200,       // Extra 200 credits if invite spends >$100
        subscriptionBonus: 100,     // Extra 100 credits/month if invite subscribes
        whaleConversionBonus: 1000 // Extra 1000 credits if invite becomes whale
      }
    };

    // Track revenue sharing
    this.revenueStats = {
      totalCommissionsPaid: 0,
      totalPassiveIncome: 0,
      topEarners: [],
      networkValue: 0
    };

    // Commission tracking
    this.pendingCommissions = new Map();
  }

  /**
   * Initialize revenue share system
   */
  async initialize() {
    console.log('💰 Initializing Viral Revenue Share System...');

    // Load existing commission data
    await this.loadCommissionData();

    // Start processing commissions
    this.startCommissionProcessing();

    console.log('✅ Revenue Share System active - 5% commissions on ALL purchases!');
  }

  /**
   * Process credit purchase and distribute commissions
   */
  async processCreditPurchase(purchaseData) {
    console.log(`💳 Processing credit purchase and calculating commissions...`);

    const {
      userId,
      amount,        // Credit amount
      value,         // Dollar value
      packageType
    } = purchaseData;

    try {
      // Get the invitation chain (who invited this user)
      const invitationChain = await this.getInvitationChain(userId);

      if (!invitationChain || invitationChain.length === 0) {
        console.log('User has no inviter, no commissions to pay');
        return { commissions: [] };
      }

      // Calculate and distribute commissions
      const commissions = await this.calculateCommissions(
        amount,
        invitationChain,
        purchaseData
      );

      // Apply commissions
      const appliedCommissions = await this.applyCommissions(commissions, purchaseData);

      // Check for bonus triggers
      const bonuses = await this.checkBonusTriggers(userId, purchaseData, invitationChain[0]);

      // Apply bonuses
      if (bonuses.length > 0) {
        await this.applyBonuses(bonuses);
      }

      // Track metrics
      await this.trackRevenueMetrics(appliedCommissions, bonuses);

      // Send notifications
      await this.sendCommissionNotifications(appliedCommissions, bonuses);

      return {
        success: true,
        commissions: appliedCommissions,
        bonuses: bonuses,
        totalDistributed: appliedCommissions.reduce((sum, c) => sum + c.amount, 0)
      };

    } catch (error) {
      console.error('Failed to process commissions:', error);
      throw error;
    }
  }

  /**
   * Calculate commissions for invitation chain
   */
  async calculateCommissions(creditAmount, invitationChain, purchaseData) {
    const commissions = [];

    // Direct inviter (Tier 1) - 5% base
    if (invitationChain[0]) {
      const inviter = invitationChain[0];
      const multiplier = await this.getCommissionMultiplier(inviter.inviterId);
      const commission = creditAmount * this.config.commissions.direct * multiplier;

      commissions.push({
        userId: inviter.inviterId,
        tier: 1,
        baseRate: this.config.commissions.direct,
        multiplier: multiplier,
        amount: Math.floor(commission),
        source: purchaseData.userId,
        type: 'direct_commission',
        description: `5% commission from ${purchaseData.userId}'s purchase`
      });
    }

    // Second tier (Tier 2) - 2% if they're gold or above
    if (invitationChain[1]) {
      const secondTierInviter = invitationChain[1];
      const inviterLevel = await this.getInviterLevel(secondTierInviter.inviterId);

      if (inviterLevel >= 'gold') {
        const commission = creditAmount * this.config.commissions.secondTier;

        commissions.push({
          userId: secondTierInviter.inviterId,
          tier: 2,
          baseRate: this.config.commissions.secondTier,
          amount: Math.floor(commission),
          source: purchaseData.userId,
          type: 'second_tier_commission',
          description: `2% tier-2 commission from network`
        });
      }
    }

    // Third tier (Tier 3) - 1% only for legends
    if (invitationChain[2]) {
      const thirdTierInviter = invitationChain[2];
      const inviterLevel = await this.getInviterLevel(thirdTierInviter.inviterId);

      if (inviterLevel === 'legend') {
        const commission = creditAmount * this.config.commissions.thirdTier;

        commissions.push({
          userId: thirdTierInviter.inviterId,
          tier: 3,
          baseRate: this.config.commissions.thirdTier,
          amount: Math.floor(commission),
          source: purchaseData.userId,
          type: 'third_tier_commission',
          description: `1% tier-3 commission (legend bonus)`
        });
      }
    }

    return commissions;
  }

  /**
   * Get commission multiplier based on inviter level
   */
  async getCommissionMultiplier(inviterId) {
    const stats = await this.getInviterStats(inviterId);
    const successfulInvites = stats.successfulInvites;

    if (successfulInvites >= 100) return this.config.commissions.multipliers.legend;  // 15%
    if (successfulInvites >= 50) return this.config.commissions.multipliers.whale;    // 12.5%
    if (successfulInvites >= 25) return this.config.commissions.multipliers.diamond;  // 10%
    if (successfulInvites >= 10) return this.config.commissions.multipliers.gold;     // 7.5%
    if (successfulInvites >= 5) return this.config.commissions.multipliers.silver;    // 6%
    return this.config.commissions.multipliers.bronze;                                // 5%
  }

  /**
   * Check for bonus triggers
   */
  async checkBonusTriggers(userId, purchaseData, directInviter) {
    const bonuses = [];

    // First purchase bonus
    const isFirstPurchase = await this.isFirstPurchase(userId);
    if (isFirstPurchase) {
      bonuses.push({
        userId: directInviter.inviterId,
        amount: this.config.bonuses.firstPurchaseBonus,
        type: 'first_purchase_bonus',
        description: `${userId} made their first purchase!`
      });
    }

    // Big spender bonus
    if (purchaseData.value >= 100) {
      bonuses.push({
        userId: directInviter.inviterId,
        amount: this.config.bonuses.bigSpenderBonus,
        type: 'big_spender_bonus',
        description: `${userId} spent over $100!`
      });
    }

    // Whale conversion bonus
    const userTotal = await this.getUserTotalSpend(userId);
    if (userTotal >= 500 && userTotal - purchaseData.value < 500) {
      bonuses.push({
        userId: directInviter.inviterId,
        amount: this.config.bonuses.whaleConversionBonus,
        type: 'whale_conversion_bonus',
        description: `${userId} became a WHALE! 🐋`
      });
    }

    return bonuses;
  }

  /**
   * Apply commissions to user accounts
   */
  async applyCommissions(commissions, purchaseData) {
    const applied = [];

    for (const commission of commissions) {
      try {
        // Add to user's credit balance
        await this.addCreditsToUser(commission.userId, commission.amount);

        // Record commission transaction
        await this.supabase.from('commission_transactions').insert({
          recipient_id: commission.userId,
          source_user_id: purchaseData.userId,
          purchase_id: purchaseData.id,
          amount: commission.amount,
          tier: commission.tier,
          rate: commission.baseRate,
          multiplier: commission.multiplier || 1,
          type: commission.type,
          description: commission.description,
          created_at: new Date().toISOString()
        });

        // Track for payout
        await this.trackForPayout(commission.userId, commission.amount);

        applied.push({
          ...commission,
          status: 'applied',
          timestamp: Date.now()
        });

        console.log(`✅ Applied ${commission.amount} credits commission to ${commission.userId}`);

      } catch (error) {
        console.error(`Failed to apply commission for ${commission.userId}:`, error);
        applied.push({
          ...commission,
          status: 'failed',
          error: error.message
        });
      }
    }

    return applied;
  }

  /**
   * Track passive income for dashboard
   */
  async getPassiveIncomeStats(userId) {
    const stats = {
      daily: 0,
      weekly: 0,
      monthly: 0,
      total: 0,
      activeInvites: 0,
      networkValue: 0,
      projectedMonthly: 0
    };

    try {
      // Get commission history
      const { data: commissions } = await this.supabase
        .from('commission_transactions')
        .select('amount, created_at')
        .eq('recipient_id', userId)
        .gte('created_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString());

      // Calculate totals
      const now = Date.now();
      const dayAgo = now - 24 * 60 * 60 * 1000;
      const weekAgo = now - 7 * 24 * 60 * 60 * 1000;

      for (const commission of commissions || []) {
        const timestamp = new Date(commission.created_at).getTime();
        stats.total += commission.amount;

        if (timestamp > dayAgo) stats.daily += commission.amount;
        if (timestamp > weekAgo) stats.weekly += commission.amount;
        stats.monthly += commission.amount;
      }

      // Get network stats
      const networkStats = await this.getNetworkStats(userId);
      stats.activeInvites = networkStats.activeUsers;
      stats.networkValue = networkStats.totalValue;

      // Project monthly income based on trends
      stats.projectedMonthly = (stats.weekly * 4.3); // Average weeks per month

      return stats;

    } catch (error) {
      console.error('Failed to get passive income stats:', error);
      return stats;
    }
  }

  /**
   * Get network statistics for an inviter
   */
  async getNetworkStats(inviterId) {
    try {
      // Get all users invited by this person
      const { data: directInvites } = await this.supabase
        .from('invitations')
        .select('invited_user_id')
        .eq('inviter_id', inviterId)
        .eq('status', 'used');

      const userIds = directInvites.map(i => i.invited_user_id);

      // Get their spending
      const { data: purchases } = await this.supabase
        .from('credit_purchases')
        .select('user_id, amount, value')
        .in('user_id', userIds);

      // Calculate totals
      const stats = {
        totalUsers: userIds.length,
        activeUsers: 0,
        totalValue: 0,
        averageSpend: 0
      };

      const uniqueActiveUsers = new Set();
      let totalSpend = 0;

      for (const purchase of purchases || []) {
        uniqueActiveUsers.add(purchase.user_id);
        totalSpend += purchase.value;
      }

      stats.activeUsers = uniqueActiveUsers.size;
      stats.totalValue = totalSpend;
      stats.averageSpend = stats.activeUsers > 0 ? totalSpend / stats.activeUsers : 0;

      return stats;

    } catch (error) {
      console.error('Failed to get network stats:', error);
      return { totalUsers: 0, activeUsers: 0, totalValue: 0, averageSpend: 0 };
    }
  }

  /**
   * Send commission notifications
   */
  async sendCommissionNotifications(commissions, bonuses) {
    for (const commission of commissions) {
      const notification = {
        userId: commission.userId,
        type: 'commission_earned',
        title: '💰 Commission Earned!',
        message: this.formatCommissionMessage(commission),
        credits: commission.amount,
        timestamp: Date.now()
      };

      this.emit('commissionEarned', notification);

      // Store notification
      await this.supabase.from('notifications').insert({
        user_id: commission.userId,
        type: notification.type,
        data: notification,
        created_at: new Date().toISOString()
      });
    }

    // Send bonus notifications
    for (const bonus of bonuses) {
      const notification = {
        userId: bonus.userId,
        type: 'bonus_earned',
        title: '🎉 Bonus Unlocked!',
        message: bonus.description,
        credits: bonus.amount,
        timestamp: Date.now()
      };

      this.emit('bonusEarned', notification);
    }
  }

  /**
   * Format commission message for notification
   */
  formatCommissionMessage(commission) {
    const messages = {
      1: `You earned ${commission.amount} credits (${(commission.baseRate * commission.multiplier * 100).toFixed(1)}% commission) from your invite's purchase!`,
      2: `Your network earned you ${commission.amount} credits! (Tier 2 commission)`,
      3: `Legend bonus! ${commission.amount} credits from your extended network!`
    };

    return messages[commission.tier] || `You earned ${commission.amount} credits!`;
  }

  /**
   * Calculate projected earnings
   */
  async calculateProjectedEarnings(inviterId) {
    const stats = await this.getPassiveIncomeStats(inviterId);
    const networkStats = await this.getNetworkStats(inviterId);

    // Assumptions for projection
    const avgPurchasePerUserPerMonth = 500; // 500 credits
    const growthRate = 1.2; // 20% monthly growth

    const projections = {
      month1: Math.floor(networkStats.activeUsers * avgPurchasePerUserPerMonth * 0.05),
      month3: Math.floor(networkStats.activeUsers * avgPurchasePerUserPerMonth * 0.05 * Math.pow(growthRate, 2) * 3),
      month6: Math.floor(networkStats.activeUsers * avgPurchasePerUserPerMonth * 0.05 * Math.pow(growthRate, 5) * 6),
      year1: Math.floor(networkStats.activeUsers * avgPurchasePerUserPerMonth * 0.05 * Math.pow(growthRate, 11) * 12),

      message: `With ${networkStats.activeUsers} active invites, you could earn ${stats.projectedMonthly} credits/month in passive income!`
    };

    return projections;
  }

  /**
   * Get leaderboard of top earners
   */
  async getTopEarners() {
    const { data: earners } = await this.supabase
      .from('commission_totals')
      .select('user_id, total_earned, network_size, username, avatar')
      .order('total_earned', { ascending: false })
      .limit(100);

    return earners.map((earner, index) => ({
      rank: index + 1,
      userId: earner.user_id,
      username: earner.username,
      avatar: earner.avatar,
      earned: earner.total_earned,
      networkSize: earner.network_size,
      monthlyPassive: Math.floor(earner.total_earned / 12), // Rough estimate
      badge: this.getEarnerBadge(earner.total_earned)
    }));
  }

  /**
   * Get earner badge based on total earnings
   */
  getEarnerBadge(totalEarned) {
    if (totalEarned >= 100000) return '💎 Diamond Earner';
    if (totalEarned >= 50000) return '👑 Royal Earner';
    if (totalEarned >= 25000) return '🏆 Champion Earner';
    if (totalEarned >= 10000) return '🥇 Gold Earner';
    if (totalEarned >= 5000) return '🥈 Silver Earner';
    return '🥉 Bronze Earner';
  }

  /**
   * Process weekly payouts
   */
  async processWeeklyPayouts() {
    console.log('💸 Processing weekly commission payouts...');

    const { data: pendingPayouts } = await this.supabase
      .from('pending_commissions')
      .select('*')
      .gte('amount', this.config.passiveIncome.minimumForPayout);

    let totalPaid = 0;

    for (const payout of pendingPayouts || []) {
      // Convert credits to cash or keep as credits based on user preference
      await this.processPayout(payout);
      totalPaid += payout.amount;
    }

    console.log(`✅ Paid out ${totalPaid} credits in commissions`);

    // Track stats
    this.revenueStats.totalCommissionsPaid += totalPaid;
  }
}

// Export singleton
const revenueShareSystem = new ViralRevenueShareSystem();
export default revenueShareSystem;