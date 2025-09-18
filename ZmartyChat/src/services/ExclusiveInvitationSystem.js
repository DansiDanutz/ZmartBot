/**
 * EXCLUSIVE INVITATION SYSTEM
 * The viral growth engine that creates worldwide addiction
 * Users can ONLY join if invited - creating massive FOMO and exclusivity
 * Inviting others rewards credits and unlocks slots
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

class ExclusiveInvitationSystem extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Invitation configuration
    this.config = {
      // Registration is CLOSED by default
      registrationOpen: false,
      inviteOnly: true,

      // Invitation rewards
      rewards: {
        perInvite: 100,           // Credits per successful invite
        milestone5: 500,          // Bonus at 5 invites
        milestone10: 1000,        // Bonus at 10 invites (+ free slot!)
        milestone25: 3000,        // Bonus at 25 invites
        milestone50: 10000,       // Bonus at 50 invites (whale status)
        milestone100: 25000       // Bonus at 100 invites (legend status)
      },

      // Slot unlocks (THE GAME CHANGER)
      slotUnlocks: {
        invites10: 1,    // 10 invites = 1 free slot forever
        invites25: 2,    // 25 invites = 2 more free slots
        invites50: 3,    // 50 invites = 3 more free slots
        invites100: 10   // 100 invites = 10 free slots (WHALE)
      },

      // Invitation limits
      limits: {
        maxInvitesPerUser: 5,        // Start with only 5 invites
        additionalPerMilestone: 2,    // Get 2 more at each milestone
        cooldownHours: 24,           // Can send 1 invite per day initially
        vipUnlimited: 50              // After 50 successful, unlimited invites
      },

      // Exclusivity levels
      exclusivityLevels: {
        founder: { min: 1, max: 100, perks: 'Founder Badge, 50% discount forever' },
        earlyAdopter: { min: 101, max: 1000, perks: '30% discount, priority alerts' },
        member: { min: 1001, max: 10000, perks: '10% discount' },
        standard: { min: 10001, max: null, perks: 'Standard pricing' }
      }
    };

    // Track invitation statistics
    this.stats = {
      totalInvitesSent: 0,
      totalInvitesAccepted: 0,
      totalUsersWaiting: 0,
      viralCoefficient: 0,
      topInviters: []
    };

    // Waiting list for people who want in but need invite
    this.waitingList = new Map();
  }

  /**
   * Initialize the invitation system
   */
  async initialize() {
    console.log('🎯 Initializing Exclusive Invitation System...');

    // Load current stats
    await this.loadInvitationStats();

    // Start monitoring invitation performance
    this.startMonitoring();

    console.log('✅ Invitation System initialized - Registration is INVITE ONLY!');
  }

  /**
   * Generate invitation code for a user
   */
  async generateInvitation(userId) {
    console.log(`🎫 Generating invitation for user ${userId}`);

    try {
      // Check if user can send invites
      const canInvite = await this.canUserInvite(userId);

      if (!canInvite.allowed) {
        return {
          success: false,
          message: canInvite.reason,
          waitTime: canInvite.waitTime
        };
      }

      // Generate unique invitation code
      const inviteCode = this.generateInviteCode();

      // Create invitation record
      const invitation = {
        code: inviteCode,
        inviter_id: userId,
        status: 'pending',
        created_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days

        // Tracking data
        metadata: {
          inviterLevel: await this.getUserLevel(userId),
          inviterInviteCount: await this.getUserInviteCount(userId),
          exclusivityTier: await this.getCurrentExclusivityTier()
        }
      };

      // Store in database
      await this.supabase.from('invitations').insert(invitation);

      // Update user's invite count
      await this.incrementUserInviteSent(userId);

      // Generate shareable link
      const inviteLink = this.generateInviteLink(inviteCode);

      return {
        success: true,
        inviteCode,
        inviteLink,
        expiresIn: '30 days',
        message: this.generateInviteMessage(invitation.metadata),
        shareText: this.generateShareText(inviteCode, invitation.metadata)
      };

    } catch (error) {
      console.error('Failed to generate invitation:', error);
      throw error;
    }
  }

  /**
   * Process invitation redemption
   */
  async redeemInvitation(inviteCode, newUserData) {
    console.log(`🎁 Processing invitation redemption: ${inviteCode}`);

    try {
      // Validate invitation
      const validation = await this.validateInvitation(inviteCode);

      if (!validation.valid) {
        return {
          success: false,
          message: validation.reason,
          waitlist: true // Offer to join waiting list
        };
      }

      const invitation = validation.invitation;

      // Create new user account
      const newUser = await this.createExclusiveUser(newUserData, invitation);

      // Reward the inviter
      const rewards = await this.rewardInviter(invitation.inviter_id, newUser.id);

      // Mark invitation as used
      await this.markInvitationUsed(inviteCode, newUser.id);

      // Check for milestone achievements
      const milestones = await this.checkMilestones(invitation.inviter_id);

      // Send notifications
      await this.sendWelcomeNotification(newUser);
      await this.sendInviterNotification(invitation.inviter_id, newUser, rewards);

      // Track viral metrics
      await this.trackViralMetrics(invitation);

      return {
        success: true,
        user: newUser,
        exclusivityLevel: newUser.exclusivityLevel,
        inviterRewards: rewards,
        milestones,
        welcomePackage: this.generateWelcomePackage(newUser),
        message: `Welcome to the exclusive club! You're member #${await this.getTotalMembers()}`
      };

    } catch (error) {
      console.error('Failed to redeem invitation:', error);
      throw error;
    }
  }

  /**
   * Reward system for inviters
   */
  async rewardInviter(inviterId, newUserId) {
    console.log(`💰 Rewarding inviter ${inviterId} for bringing ${newUserId}`);

    const rewards = {
      credits: 0,
      bonuses: [],
      unlockedSlots: 0,
      newPrivileges: []
    };

    try {
      // Get inviter's current stats
      const inviterStats = await this.getInviterStats(inviterId);
      const successfulInvites = inviterStats.successfulInvites + 1;

      // Base reward
      rewards.credits += this.config.rewards.perInvite;

      // Milestone bonuses
      if (successfulInvites === 5) {
        rewards.credits += this.config.rewards.milestone5;
        rewards.bonuses.push('🎉 5 Invites Milestone! +500 bonus credits!');
      }

      if (successfulInvites === 10) {
        rewards.credits += this.config.rewards.milestone10;
        rewards.unlockedSlots += 1;
        rewards.bonuses.push('🔓 10 Invites! FREE SLOT UNLOCKED + 1000 credits!');
        rewards.newPrivileges.push('slot_unlock');
      }

      if (successfulInvites === 25) {
        rewards.credits += this.config.rewards.milestone25;
        rewards.unlockedSlots += 2;
        rewards.bonuses.push('💎 25 Invites! 2 MORE SLOTS + 3000 credits!');
        rewards.newPrivileges.push('premium_alerts');
      }

      if (successfulInvites === 50) {
        rewards.credits += this.config.rewards.milestone50;
        rewards.unlockedSlots += 3;
        rewards.bonuses.push('🐋 50 Invites! WHALE STATUS + 10000 credits!');
        rewards.newPrivileges.push('whale_status', 'unlimited_invites');
      }

      if (successfulInvites === 100) {
        rewards.credits += this.config.rewards.milestone100;
        rewards.unlockedSlots += 10;
        rewards.bonuses.push('👑 100 Invites! LEGEND STATUS + 25000 credits!');
        rewards.newPrivileges.push('legend_status', 'vip_support', 'custom_strategies');
      }

      // Apply credits
      await this.addCredits(inviterId, rewards.credits);

      // Unlock slots
      if (rewards.unlockedSlots > 0) {
        await this.unlockSlots(inviterId, rewards.unlockedSlots);
      }

      // Update inviter stats
      await this.updateInviterStats(inviterId, successfulInvites);

      // Create reward notification
      await this.createRewardNotification(inviterId, rewards);

      return rewards;

    } catch (error) {
      console.error('Failed to reward inviter:', error);
      throw error;
    }
  }

  /**
   * Check if user can send invitations
   */
  async canUserInvite(userId) {
    const userStats = await this.getInviterStats(userId);

    // Check cooldown
    const lastInvite = userStats.lastInviteSent;
    const cooldownHours = this.config.limits.cooldownHours;
    const hoursSinceLastInvite = (Date.now() - new Date(lastInvite).getTime()) / (1000 * 60 * 60);

    if (hoursSinceLastInvite < cooldownHours && userStats.successfulInvites < 10) {
      return {
        allowed: false,
        reason: `Cooldown active. Wait ${Math.ceil(cooldownHours - hoursSinceLastInvite)} hours`,
        waitTime: (cooldownHours - hoursSinceLastInvite) * 60 * 60 * 1000
      };
    }

    // Check invite limit
    const maxInvites = this.calculateMaxInvites(userStats.successfulInvites);
    if (userStats.totalInvitesSent >= maxInvites && userStats.successfulInvites < this.config.limits.vipUnlimited) {
      return {
        allowed: false,
        reason: `Invite limit reached. Get ${10 - userStats.successfulInvites} more successful invites to unlock more`,
        waitTime: null
      };
    }

    return { allowed: true };
  }

  /**
   * Join waiting list (for those without invites)
   */
  async joinWaitingList(email, userData) {
    console.log(`⏳ Adding ${email} to waiting list`);

    const waitlistEntry = {
      email,
      userData,
      joinedAt: Date.now(),
      position: this.waitingList.size + 1,
      estimatedWait: this.estimateWaitTime(),
      referralSource: userData.referralSource || 'organic'
    };

    // Store in database
    await this.supabase.from('waiting_list').insert({
      email,
      data: waitlistEntry,
      created_at: new Date().toISOString()
    });

    // Add to memory
    this.waitingList.set(email, waitlistEntry);

    // Send confirmation email
    await this.sendWaitlistConfirmation(email, waitlistEntry);

    return {
      success: true,
      position: waitlistEntry.position,
      estimatedWait: waitlistEntry.estimatedWait,
      message: `You're #${waitlistEntry.position} on the waiting list. Find someone with an invite to skip the line!`,
      tips: [
        'Ask friends who are already members',
        'Check social media for invite codes',
        'Join our Discord to network with members'
      ]
    };
  }

  /**
   * Generate viral share content
   */
  generateShareText(inviteCode, metadata) {
    const templates = [
      `🔥 I just got access to Zmarty - the AI that predicts crypto with 87% accuracy! Only ${100 - metadata.inviterLevel} spots left at founder price. Use my code: ${inviteCode}`,

      `💎 EXCLUSIVE: I'm one of the first ${metadata.inviterLevel * 10} users of Zmarty. It's already found me 3 profitable setups this week. Want in? ${inviteCode}`,

      `🚀 This is insane! Zmarty just alerted me to a pattern with 92% historical success rate. I have ${5 - metadata.inviterInviteCount} invites left: ${inviteCode}`,

      `⚡ Can't believe I got early access to Zmarty! It analyzes 4 years of data to find profitable patterns. Invite-only right now: ${inviteCode}`,

      `🎯 Just made 5.7% in 2 days following Zmarty triggers. I can invite ${5 - metadata.inviterInviteCount} more people. First come, first served: ${inviteCode}`
    ];

    // Pick random template
    const template = templates[Math.floor(Math.random() * templates.length)];

    return {
      twitter: template,
      telegram: `${template}\n\nJoin here: ${this.generateInviteLink(inviteCode)}`,
      discord: `**EXCLUSIVE INVITE**\n${template}\n\n**Limited time:** Expires in 30 days\n**Perks:** Founder pricing, priority alerts\n**Code:** ||${inviteCode}||`,
      whatsapp: template
    };
  }

  /**
   * Gamification: Leaderboard of top inviters
   */
  async getInviterLeaderboard() {
    const { data: leaderboard } = await this.supabase
      .from('user_invitation_stats')
      .select('user_id, successful_invites, total_rewards, username, avatar')
      .order('successful_invites', { ascending: false })
      .limit(100);

    return leaderboard.map((user, index) => ({
      rank: index + 1,
      userId: user.user_id,
      username: user.username,
      avatar: user.avatar,
      invites: user.successful_invites,
      rewards: user.total_rewards,
      status: this.getInviterStatus(user.successful_invites),
      badge: this.getInviterBadge(user.successful_invites)
    }));
  }

  /**
   * Get inviter status based on successful invites
   */
  getInviterStatus(inviteCount) {
    if (inviteCount >= 100) return '👑 LEGEND';
    if (inviteCount >= 50) return '🐋 WHALE';
    if (inviteCount >= 25) return '💎 DIAMOND';
    if (inviteCount >= 10) return '🥇 GOLD';
    if (inviteCount >= 5) return '🥈 SILVER';
    return '🥉 BRONZE';
  }

  /**
   * Calculate viral coefficient
   */
  async calculateViralCoefficient() {
    // Viral Coefficient = (Number of invites sent per user) × (Conversion rate)
    const avgInvitesPerUser = this.stats.totalInvitesSent / (await this.getTotalMembers());
    const conversionRate = this.stats.totalInvitesAccepted / this.stats.totalInvitesSent;

    const viralCoefficient = avgInvitesPerUser * conversionRate;

    // > 1 means viral growth
    return {
      coefficient: viralCoefficient,
      status: viralCoefficient > 1 ? 'VIRAL' : 'GROWING',
      avgInvitesPerUser,
      conversionRate,
      projection: this.projectGrowth(viralCoefficient)
    };
  }

  /**
   * Project growth based on viral coefficient
   */
  projectGrowth(coefficient) {
    const currentUsers = 100; // Starting with 100 users
    const projections = [];

    let users = currentUsers;
    for (let month = 1; month <= 12; month++) {
      users = users * Math.pow(1 + coefficient, 1);
      projections.push({
        month,
        users: Math.floor(users),
        revenue: Math.floor(users * 75) // $75 average per user
      });
    }

    return projections;
  }

  /**
   * Create urgency with limited spots
   */
  async getCurrentAvailability() {
    const totalMembers = await this.getTotalMembers();
    const currentTier = this.getCurrentExclusivityTier();

    return {
      currentMembers: totalMembers,
      currentTier: currentTier.name,
      spotsRemaining: currentTier.max - totalMembers,
      nextTierIn: currentTier.max - totalMembers,
      message: this.generateUrgencyMessage(currentTier, totalMembers)
    };
  }

  /**
   * Generate urgency message
   */
  generateUrgencyMessage(tier, totalMembers) {
    const spotsLeft = tier.max - totalMembers;

    if (spotsLeft < 10) {
      return `🔥 ONLY ${spotsLeft} FOUNDER SPOTS LEFT! Next tier pays 50% more!`;
    }

    if (spotsLeft < 50) {
      return `⚡ ${spotsLeft} spots remaining at ${tier.name} pricing. Hurry!`;
    }

    if (spotsLeft < 100) {
      return `📈 Join now while ${tier.name} pricing is still available`;
    }

    return `🎯 Exclusive ${tier.name} membership available`;
  }

  /**
   * Generate unique invite code
   */
  generateInviteCode() {
    // Format: ZMRT-XXXX-XXXX-XXXX
    const segments = [];
    segments.push('ZMRT');

    for (let i = 0; i < 3; i++) {
      segments.push(
        crypto.randomBytes(2)
          .toString('hex')
          .toUpperCase()
      );
    }

    return segments.join('-');
  }

  /**
   * Generate invite link
   */
  generateInviteLink(code) {
    return `https://zmarty.ai/exclusive/${code}`;
  }

  /**
   * Get current exclusivity tier
   */
  async getCurrentExclusivityTier() {
    const totalMembers = await this.getTotalMembers();

    for (const [name, tier] of Object.entries(this.config.exclusivityLevels)) {
      if (totalMembers >= tier.min && (tier.max === null || totalMembers <= tier.max)) {
        return { name, ...tier };
      }
    }

    return this.config.exclusivityLevels.standard;
  }

  /**
   * Get total member count
   */
  async getTotalMembers() {
    const { count } = await this.supabase
      .from('users')
      .select('id', { count: 'exact' });

    return count || 0;
  }

  /**
   * Track viral metrics
   */
  async trackViralMetrics(invitation) {
    // Update stats
    this.stats.totalInvitesAccepted++;

    // Calculate viral coefficient
    const viral = await this.calculateViralCoefficient();
    this.stats.viralCoefficient = viral.coefficient;

    // Store metrics
    await this.supabase.from('viral_metrics').insert({
      date: new Date().toISOString(),
      invites_sent: this.stats.totalInvitesSent,
      invites_accepted: this.stats.totalInvitesAccepted,
      viral_coefficient: viral.coefficient,
      conversion_rate: viral.conversionRate
    });

    // Emit event for monitoring
    this.emit('viralMetrics', viral);
  }
}

// Export singleton
const invitationSystem = new ExclusiveInvitationSystem();
export default invitationSystem;