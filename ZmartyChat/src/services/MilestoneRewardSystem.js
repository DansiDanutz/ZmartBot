/**
 * MILESTONE REWARD SYSTEM
 * Multiple targets keep users constantly engaged and working
 * Each milestone unlocks new benefits, creating continuous motivation
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';

class MilestoneRewardSystem extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // COMPREHENSIVE MILESTONE STRUCTURE
    this.milestones = {
      // 🎯 MILESTONE 1: STARTER (1 invite)
      milestone_1: {
        invitesRequired: 1,
        commission: 0.05, // 5%
        rewards: {
          credits: 50,
          badge: '🌱 First Steps',
          title: 'Network Starter'
        },
        unlocks: [
          'Basic dashboard',
          'View your earnings',
          'Share tracking'
        ],
        message: '🎉 First invite successful! Welcome to the network!'
      },

      // 🎯 MILESTONE 5: ACTIVE (5 invites)
      milestone_5: {
        invitesRequired: 5,
        commission: 0.06, // 6%
        rewards: {
          credits: 300,
          badge: '⚡ Active Inviter',
          title: 'Network Builder',
          extraInvites: 5
        },
        unlocks: [
          'Earnings analytics',
          '5 additional invite codes',
          'Weekly payout option'
        ],
        message: '⚡ 5 invites! You\'re building momentum!'
      },

      // 🎯 MILESTONE 10: POWER USER (10 invites)
      milestone_10: {
        invitesRequired: 10,
        commission: 0.08, // 8%
        rewards: {
          credits: 1000,
          badge: '🔥 Power User',
          title: 'Growth Driver',
          freeSlot: 1
        },
        unlocks: [
          '🎰 1 FREE SLOT FOREVER',
          'Custom referral link',
          'Network growth chart',
          'Priority support'
        ],
        message: '🔥 10 INVITES! FREE SLOT UNLOCKED + 8% commission!'
      },

      // 🎯 MILESTONE 25: SILVER (25 invites)
      milestone_25: {
        invitesRequired: 25,
        commission: 0.10, // 10%
        rewards: {
          credits: 3000,
          badge: '🥈 Silver Elite',
          title: 'Network Expert',
          freeSlots: 2,
          extraInvites: 10
        },
        unlocks: [
          '🎰 2 MORE FREE SLOTS',
          'Instant payouts',
          'Custom promo codes',
          'Tier 2 commissions (2% from sub-network)'
        ],
        message: '🥈 25 INVITES! DOUBLE COMMISSION (10%) + 2 free slots!'
      },

      // 🎯 MILESTONE 50: GOLD (50 invites)
      milestone_50: {
        invitesRequired: 50,
        commission: 0.12, // 12%
        rewards: {
          credits: 8000,
          badge: '🥇 Gold Elite',
          title: 'Growth Champion',
          freeSlots: 3,
          cashWithdrawal: true
        },
        unlocks: [
          '💰 CASH WITHDRAWALS ENABLED',
          '🎰 3 MORE FREE SLOTS',
          'Custom landing page',
          'API access beta',
          'Unlimited invites'
        ],
        message: '🥇 50 INVITES! 12% commission + CASH WITHDRAWALS!'
      },

      // 🎯 MILESTONE 75: PLATINUM (75 invites)
      milestone_75: {
        invitesRequired: 75,
        commission: 0.13, // 13%
        rewards: {
          credits: 15000,
          badge: '💎 Platinum Elite',
          title: 'Network Leader',
          freeSlots: 5,
          whiteLabel: 'basic'
        },
        unlocks: [
          '🎰 5 MORE FREE SLOTS (Total: 11)',
          'Basic white label options',
          'Dedicated account manager',
          'Monthly strategy calls',
          'Early feature access'
        ],
        message: '💎 75 INVITES! Platinum status achieved!'
      },

      // 🎯 MILESTONE 100: INFLUENCER (100 invites)
      milestone_100: {
        invitesRequired: 100,
        commission: 0.15, // 15%
        rewards: {
          credits: 25000,
          badge: '👑 Influencer',
          title: 'Elite Influencer',
          freeSlots: 10,
          monthlyBonus: 1000
        },
        unlocks: [
          '👑 INFLUENCER STATUS',
          '🎰 10 MORE FREE SLOTS (Total: 21)',
          'Full white label platform',
          'Custom email domain',
          'Video testimonial request',
          'Speaker opportunities',
          'Tier 3 commissions (1% from extended network)'
        ],
        message: '👑 100 INVITES! INFLUENCER STATUS UNLOCKED! 15% commission!'
      },

      // 🎯 MILESTONE 250: AMBASSADOR (250 invites)
      milestone_250: {
        invitesRequired: 250,
        commission: 0.17, // 17%
        rewards: {
          credits: 50000,
          badge: '🌟 Ambassador',
          title: 'Brand Ambassador',
          freeSlots: 25,
          equityOption: true
        },
        unlocks: [
          '🌟 BRAND AMBASSADOR',
          '🎰 25 MORE FREE SLOTS (Total: 46)',
          'Equity participation option',
          'Co-marketing opportunities',
          'Conference speaking slots',
          'Product development input'
        ],
        message: '🌟 250 INVITES! Ambassador status - You\'re part of the team!'
      },

      // 🎯 MILESTONE 500: LEGEND (500 invites)
      milestone_500: {
        invitesRequired: 500,
        commission: 0.20, // 20%
        rewards: {
          credits: 100000,
          badge: '🏆 Legend',
          title: 'Network Legend',
          freeSlots: 50,
          lifetimeRevShare: true
        },
        unlocks: [
          '🏆 LEGEND STATUS',
          '🎰 50 MORE FREE SLOTS (Total: 96)',
          '20% COMMISSION FOREVER',
          'Lifetime revenue share',
          'Advisory board invitation',
          'Exclusive Legend events',
          'Your name in the platform'
        ],
        message: '🏆 500 INVITES! LEGEND STATUS - Maximum commission 20%!'
      },

      // 🎯 MILESTONE 1000: FOUNDER PARTNER (1000 invites)
      milestone_1000: {
        invitesRequired: 1000,
        commission: 0.25, // 25% - exclusive tier
        rewards: {
          credits: 250000,
          badge: '💫 Founder Partner',
          title: 'Founding Partner',
          freeSlots: 'unlimited',
          equity: '0.1%'
        },
        unlocks: [
          '💫 FOUNDING PARTNER STATUS',
          '♾️ UNLIMITED FREE SLOTS',
          '25% COMMISSION - EXCLUSIVE RATE',
          '0.1% EQUITY IN COMPANY',
          'Board observer rights',
          'Monthly dividends',
          'Exit participation'
        ],
        message: '💫 1000 INVITES! FOUNDING PARTNER - You\'re a co-owner!'
      }
    };

    // Track user progress
    this.userProgress = new Map();

    // Leaderboard data
    this.leaderboard = [];
  }

  /**
   * Check and award milestones for a user
   */
  async checkMilestones(userId, currentInvites) {
    console.log(`🎯 Checking milestones for ${userId} with ${currentInvites} invites`);

    const achievedMilestones = [];
    const upcomingMilestones = [];

    for (const [key, milestone] of Object.entries(this.milestones)) {
      if (currentInvites >= milestone.invitesRequired) {
        // Check if already achieved
        const alreadyAchieved = await this.hasMilestoneBeenAchieved(userId, key);

        if (!alreadyAchieved) {
          // New milestone achieved!
          achievedMilestones.push({
            key,
            milestone,
            isNew: true
          });

          // Award milestone
          await this.awardMilestone(userId, key, milestone);
        } else {
          achievedMilestones.push({
            key,
            milestone,
            isNew: false
          });
        }
      } else {
        // Upcoming milestone
        upcomingMilestones.push({
          key,
          milestone,
          invitesNeeded: milestone.invitesRequired - currentInvites,
          progress: (currentInvites / milestone.invitesRequired) * 100
        });
      }
    }

    // Get next milestone
    const nextMilestone = upcomingMilestones[0];

    return {
      currentInvites,
      achievedMilestones,
      nextMilestone,
      totalMilestones: Object.keys(this.milestones).length,
      achievedCount: achievedMilestones.length,
      progressToNext: nextMilestone ? nextMilestone.progress : 100
    };
  }

  /**
   * Award milestone rewards to user
   */
  async awardMilestone(userId, milestoneKey, milestone) {
    console.log(`🏆 Awarding ${milestoneKey} to ${userId}!`);

    try {
      // Award credits
      if (milestone.rewards.credits) {
        await this.awardCredits(userId, milestone.rewards.credits);
      }

      // Award free slots
      if (milestone.rewards.freeSlot) {
        await this.unlockFreeSlots(userId, milestone.rewards.freeSlot);
      } else if (milestone.rewards.freeSlots) {
        await this.unlockFreeSlots(userId, milestone.rewards.freeSlots);
      }

      // Update commission rate
      await this.updateCommissionRate(userId, milestone.commission);

      // Award badge and title
      await this.awardBadgeAndTitle(userId, milestone.rewards.badge, milestone.rewards.title);

      // Enable special features
      if (milestone.rewards.cashWithdrawal) {
        await this.enableCashWithdrawals(userId);
      }

      if (milestone.rewards.whiteLabel) {
        await this.enableWhiteLabel(userId, milestone.rewards.whiteLabel);
      }

      if (milestone.rewards.equityOption) {
        await this.offerEquityOption(userId);
      }

      // Record achievement
      await this.recordAchievement(userId, milestoneKey, milestone);

      // Send celebration notification
      await this.sendCelebrationNotification(userId, milestone);

      // Emit event for real-time updates
      this.emit('milestoneAchieved', {
        userId,
        milestone: milestoneKey,
        rewards: milestone.rewards,
        message: milestone.message
      });

      return {
        success: true,
        milestone: milestoneKey,
        rewards: milestone.rewards,
        message: milestone.message
      };

    } catch (error) {
      console.error('Failed to award milestone:', error);
      throw error;
    }
  }

  /**
   * Generate milestone progress dashboard
   */
  async getMilestoneProgress(userId) {
    const stats = await this.getUserStats(userId);
    const currentInvites = stats.successfulInvites;

    const progress = {
      currentInvites,
      currentCommission: await this.getCurrentCommissionRate(userId),
      totalEarned: stats.totalEarnings,

      // Visual progress bar data
      milestoneProgress: [],

      // Next goals
      nextMilestones: [],

      // Motivation
      motivationalMessage: '',

      // Comparison
      percentile: await this.getUserPercentile(userId),
      averageInvites: await this.getAverageInvites(),

      // Achievements
      badges: [],
      titles: []
    };

    // Calculate progress for each milestone
    for (const [key, milestone] of Object.entries(this.milestones)) {
      const achieved = currentInvites >= milestone.invitesRequired;
      const progressPercent = Math.min(100, (currentInvites / milestone.invitesRequired) * 100);

      progress.milestoneProgress.push({
        milestone: key,
        target: milestone.invitesRequired,
        achieved,
        progress: progressPercent,
        commission: `${milestone.commission * 100}%`,
        mainReward: this.getMainReward(milestone)
      });

      // Add to next milestones if not achieved
      if (!achieved) {
        progress.nextMilestones.push({
          target: milestone.invitesRequired,
          invitesNeeded: milestone.invitesRequired - currentInvites,
          reward: this.getMainReward(milestone),
          commission: `${milestone.commission * 100}%`,
          daysToAchieve: this.estimateDaysToAchieve(userId, milestone.invitesRequired)
        });
      }
    }

    // Generate motivational message
    progress.motivationalMessage = this.generateMotivationalMessage(currentInvites, progress.nextMilestones[0]);

    // Get badges and titles
    progress.badges = await this.getUserBadges(userId);
    progress.titles = await this.getUserTitles(userId);

    return progress;
  }

  /**
   * Get main reward description for milestone
   */
  getMainReward(milestone) {
    if (milestone.rewards.freeSlots === 'unlimited') {
      return '♾️ UNLIMITED SLOTS';
    }
    if (milestone.rewards.equity) {
      return `${milestone.rewards.equity} EQUITY`;
    }
    if (milestone.rewards.lifetimeRevShare) {
      return 'LIFETIME REVENUE SHARE';
    }
    if (milestone.rewards.freeSlots >= 10) {
      return `${milestone.rewards.freeSlots} FREE SLOTS`;
    }
    if (milestone.rewards.cashWithdrawal) {
      return '💰 CASH WITHDRAWALS';
    }
    if (milestone.rewards.freeSlot || milestone.rewards.freeSlots) {
      const slots = milestone.rewards.freeSlot || milestone.rewards.freeSlots;
      return `${slots} FREE SLOT${slots > 1 ? 'S' : ''}`;
    }
    return `${milestone.rewards.credits} CREDITS`;
  }

  /**
   * Generate motivational message based on progress
   */
  generateMotivationalMessage(currentInvites, nextMilestone) {
    if (!nextMilestone) {
      return '🏆 LEGEND! You\'ve achieved all milestones! Keep growing your empire!';
    }

    const messages = {
      close: [
        `🔥 Just ${nextMilestone.invitesNeeded} more invites to unlock ${nextMilestone.reward}!`,
        `⚡ You're SO CLOSE! ${nextMilestone.invitesNeeded} invites to ${nextMilestone.commission} commission!`,
        `💪 Push for ${nextMilestone.invitesNeeded} more! ${nextMilestone.reward} is within reach!`
      ],
      medium: [
        `📈 ${nextMilestone.invitesNeeded} invites to your next milestone: ${nextMilestone.reward}`,
        `🎯 Target: ${nextMilestone.target} invites for ${nextMilestone.commission} commission`,
        `💰 Work towards ${nextMilestone.reward} - only ${nextMilestone.invitesNeeded} to go!`
      ],
      far: [
        `🚀 Your journey to ${nextMilestone.reward} starts now!`,
        `🌟 Build your network to ${nextMilestone.target} invites for amazing rewards!`,
        `📊 Grow steadily towards ${nextMilestone.commission} commission rate!`
      ]
    };

    let messageType = 'far';
    if (nextMilestone.invitesNeeded <= 5) messageType = 'close';
    else if (nextMilestone.invitesNeeded <= 20) messageType = 'medium';

    const messageList = messages[messageType];
    return messageList[Math.floor(Math.random() * messageList.length)];
  }

  /**
   * Calculate leaderboard with milestone context
   */
  async generateLeaderboard() {
    const { data: users } = await this.supabase
      .from('user_invitation_stats')
      .select('*')
      .order('successful_invites', { ascending: false })
      .limit(100);

    const leaderboard = [];

    for (const [index, user] of users.entries()) {
      const milestone = this.getCurrentMilestoneForInvites(user.successful_invites);
      const nextMilestone = this.getNextMilestoneForInvites(user.successful_invites);

      leaderboard.push({
        rank: index + 1,
        userId: user.user_id,
        username: user.username,
        avatar: user.avatar,
        invites: user.successful_invites,

        // Milestone info
        currentMilestone: milestone?.rewards.title || 'Getting Started',
        currentBadge: milestone?.rewards.badge || '🌱',
        commission: `${(milestone?.commission || 0.05) * 100}%`,

        // Progress to next
        nextTarget: nextMilestone?.invitesRequired,
        progressToNext: nextMilestone ?
          ((user.successful_invites / nextMilestone.invitesRequired) * 100).toFixed(1) + '%' :
          'MAX',

        // Earnings
        totalEarnings: user.total_earnings,
        monthlyPassive: user.monthly_passive,

        // Special badges
        specialBadges: this.getSpecialBadges(user)
      });
    }

    return leaderboard;
  }

  /**
   * Get current milestone for invite count
   */
  getCurrentMilestoneForInvites(inviteCount) {
    let currentMilestone = null;

    for (const milestone of Object.values(this.milestones)) {
      if (inviteCount >= milestone.invitesRequired) {
        currentMilestone = milestone;
      } else {
        break;
      }
    }

    return currentMilestone;
  }

  /**
   * Get next milestone for invite count
   */
  getNextMilestoneForInvites(inviteCount) {
    for (const milestone of Object.values(this.milestones)) {
      if (inviteCount < milestone.invitesRequired) {
        return milestone;
      }
    }
    return null;
  }

  /**
   * Create milestone achievement notification
   */
  async sendCelebrationNotification(userId, milestone) {
    const notification = {
      type: 'milestone_achieved',
      priority: 'high',

      title: `🎉 ${milestone.rewards.badge} ACHIEVED!`,

      message: milestone.message,

      details: {
        newCommission: `${milestone.commission * 100}%`,
        rewards: milestone.rewards,
        unlocks: milestone.unlocks
      },

      actions: [
        {
          label: 'View Rewards',
          action: 'view_rewards'
        },
        {
          label: 'Share Achievement',
          action: 'share_achievement'
        }
      ],

      celebrationType: this.getCelebrationType(milestone.invitesRequired),

      shareText: this.generateShareText(userId, milestone)
    };

    // Send notification
    this.emit('celebration', notification);

    // Store in database
    await this.supabase.from('notifications').insert({
      user_id: userId,
      type: 'milestone_achieved',
      data: notification,
      created_at: new Date().toISOString()
    });
  }

  /**
   * Generate share text for milestone achievement
   */
  generateShareText(userId, milestone) {
    const templates = [
      `🎉 Just unlocked ${milestone.rewards.badge} on @ZmartyAI! Now earning ${milestone.commission * 100}% commission on all referrals! 🚀`,

      `💪 Milestone achieved! ${milestone.invitesRequired} successful invites on Zmarty. ${this.getMainReward(milestone)} unlocked! Who wants an invite? 👀`,

      `🏆 Level up! Now a ${milestone.rewards.title} on @ZmartyAI with ${milestone.commission * 100}% commission rate. The grind pays off! 💰`
    ];

    return templates[Math.floor(Math.random() * templates.length)];
  }

  /**
   * Get celebration type based on milestone importance
   */
  getCelebrationType(invitesRequired) {
    if (invitesRequired >= 500) return 'legendary';
    if (invitesRequired >= 100) return 'epic';
    if (invitesRequired >= 50) return 'major';
    if (invitesRequired >= 25) return 'significant';
    if (invitesRequired >= 10) return 'important';
    return 'standard';
  }
}

// Export singleton
const milestoneSystem = new MilestoneRewardSystem();
export default milestoneSystem;