/**
 * KNOWLEDGE VALIDATOR AGENT
 * Validates incoming knowledge for accuracy, duplicates, and quality
 * Ensures only high-quality, verified information enters the brain
 */

import BaseAgent from './BaseAgent.js';
import crypto from 'crypto';
import stringSimilarity from 'string-similarity';

export default class KnowledgeValidatorAgent extends BaseAgent {
  constructor(config) {
    super({
      ...config,
      name: 'Knowledge Validator Agent',
      priority: 10 // Highest priority - first line of defense
    });

    // Validation rules
    this.validationRules = {
      minConfidence: 0.3,
      duplicateThreshold: 0.85,
      minContentLength: 50,
      maxContentLength: 50000,
      requiredFields: ['title', 'content', 'source_type'],
      trustedSources: ['manual', 'api', 'backtest', 'market_analysis'],
      suspiciousSources: ['external', 'user_interaction']
    };

    // Cache for recent validations
    this.validationCache = new Map();
    this.duplicateCache = new Map();

    // Validation statistics
    this.stats = {
      totalValidated: 0,
      approved: 0,
      rejected: 0,
      duplicates: 0,
      conflicts: 0
    };
  }

  /**
   * Initialize the validator
   */
  async initialize() {
    console.log('🔍 Initializing Knowledge Validator Agent');

    // Load existing knowledge hashes for duplicate detection
    await this.loadKnowledgeHashes();

    // Load validation patterns
    await this.loadValidationPatterns();
  }

  /**
   * Execute validation task
   */
  async executeTask(task) {
    const { type, data } = task;

    switch (type) {
      case 'validate_knowledge':
        return await this.validateKnowledge(data);

      case 'validate_pattern':
        return await this.validatePattern(data);

      case 'validate_batch':
        return await this.validateBatch(data);

      case 'check_conflicts':
        return await this.checkConflicts(data);

      default:
        throw new Error(`Unknown task type: ${type}`);
    }
  }

  /**
   * Scheduled validation tasks
   */
  async executeScheduledTasks() {
    // Re-validate low confidence knowledge
    await this.revalidateLowConfidence();

    // Check for outdated validations
    await this.checkOutdatedValidations();

    // Clean validation cache
    this.cleanCache();
  }

  /**
   * Validate incoming knowledge
   */
  async validateKnowledge(knowledge) {
    const validationResult = {
      isValid: true,
      confidence: 1.0,
      issues: [],
      suggestions: [],
      metadata: {}
    };

    try {
      this.stats.totalValidated++;

      // Step 1: Basic validation
      const basicValidation = this.validateBasicRequirements(knowledge);
      if (!basicValidation.isValid) {
        validationResult.isValid = false;
        validationResult.issues.push(...basicValidation.issues);
        validationResult.confidence *= 0.5;
      }

      // Step 2: Check for duplicates
      const duplicateCheck = await this.checkDuplicates(knowledge);
      if (duplicateCheck.isDuplicate) {
        validationResult.isValid = false;
        validationResult.issues.push(`Duplicate of ${duplicateCheck.originalId}`);
        validationResult.metadata.duplicate = duplicateCheck;
        this.stats.duplicates++;
      }

      // Step 3: Content validation
      const contentValidation = await this.validateContent(knowledge);
      validationResult.confidence *= contentValidation.confidence;
      if (contentValidation.issues.length > 0) {
        validationResult.issues.push(...contentValidation.issues);
      }

      // Step 4: Source credibility
      const sourceCredibility = this.assessSourceCredibility(knowledge.source_type);
      validationResult.confidence *= sourceCredibility;

      // Step 5: Check for conflicts
      const conflicts = await this.detectConflicts(knowledge);
      if (conflicts.length > 0) {
        validationResult.issues.push('Conflicts detected');
        validationResult.metadata.conflicts = conflicts;
        this.stats.conflicts++;
      }

      // Step 6: Category validation
      if (knowledge.category_id) {
        const categoryValid = await this.validateCategory(knowledge.category_id);
        if (!categoryValid) {
          validationResult.issues.push('Invalid category');
        }
      }

      // Step 7: Calculate final confidence
      validationResult.confidence = this.calculateFinalConfidence(
        validationResult,
        knowledge
      );

      // Determine final validity
      if (validationResult.confidence < this.validationRules.minConfidence) {
        validationResult.isValid = false;
        validationResult.issues.push('Confidence too low');
      }

      // Store validation result
      await this.storeValidationResult(knowledge, validationResult);

      // Update statistics
      if (validationResult.isValid) {
        this.stats.approved++;
        this.sendMessage('knowledge:validated', {
          knowledge,
          validation: validationResult
        });
      } else {
        this.stats.rejected++;
        this.sendMessage('knowledge:rejected', {
          knowledge,
          validation: validationResult
        });
      }

      // Log activity
      await this.logActivity('knowledge_validation', {
        knowledgeId: knowledge.id,
        result: validationResult
      });

      return validationResult;

    } catch (error) {
      this.handleError('Knowledge validation failed', error);
      validationResult.isValid = false;
      validationResult.issues.push(`Validation error: ${error.message}`);
      return validationResult;
    }
  }

  /**
   * Validate basic requirements
   */
  validateBasicRequirements(knowledge) {
    const result = {
      isValid: true,
      issues: []
    };

    // Check required fields
    for (const field of this.validationRules.requiredFields) {
      if (!knowledge[field]) {
        result.isValid = false;
        result.issues.push(`Missing required field: ${field}`);
      }
    }

    // Check content length
    if (knowledge.content) {
      const length = knowledge.content.length;
      if (length < this.validationRules.minContentLength) {
        result.issues.push('Content too short');
      }
      if (length > this.validationRules.maxContentLength) {
        result.issues.push('Content too long');
      }
    }

    // Check title validity
    if (knowledge.title && knowledge.title.length < 3) {
      result.issues.push('Title too short');
    }

    return result;
  }

  /**
   * Check for duplicate knowledge
   */
  async checkDuplicates(knowledge) {
    // Generate content hash
    const contentHash = this.generateContentHash(knowledge.content);

    // Check cache first
    if (this.duplicateCache.has(contentHash)) {
      return {
        isDuplicate: true,
        originalId: this.duplicateCache.get(contentHash)
      };
    }

    // Check database for exact match
    const { data: exactMatch } = await this.supabase
      .from('brain_knowledge')
      .select('id, title')
      .eq('content_hash', contentHash)
      .single();

    if (exactMatch) {
      this.duplicateCache.set(contentHash, exactMatch.id);
      return {
        isDuplicate: true,
        originalId: exactMatch.id
      };
    }

    // Check for similar content
    const { data: similarContent } = await this.supabase
      .from('brain_knowledge')
      .select('id, title, content')
      .eq('knowledge_type', knowledge.knowledge_type)
      .limit(20);

    if (similarContent) {
      for (const item of similarContent) {
        const similarity = stringSimilarity.compareTwoStrings(
          knowledge.content.substring(0, 1000),
          item.content.substring(0, 1000)
        );

        if (similarity > this.validationRules.duplicateThreshold) {
          return {
            isDuplicate: true,
            originalId: item.id,
            similarity: similarity
          };
        }
      }
    }

    return { isDuplicate: false };
  }

  /**
   * Validate content quality
   */
  async validateContent(knowledge) {
    const result = {
      confidence: 1.0,
      issues: []
    };

    // Check for spam patterns
    if (this.detectSpamPatterns(knowledge.content)) {
      result.confidence *= 0.3;
      result.issues.push('Spam patterns detected');
    }

    // Check for harmful content
    if (this.detectHarmfulContent(knowledge.content)) {
      result.confidence = 0;
      result.issues.push('Harmful content detected');
    }

    // Check information quality
    const qualityScore = await this.assessInformationQuality(knowledge);
    result.confidence *= qualityScore;

    if (qualityScore < 0.5) {
      result.issues.push('Low information quality');
    }

    // Check formatting
    if (!this.isWellFormatted(knowledge.content)) {
      result.confidence *= 0.9;
      result.issues.push('Poor formatting');
    }

    return result;
  }

  /**
   * Detect conflicts with existing knowledge
   */
  async detectConflicts(knowledge) {
    const conflicts = [];

    // Search for contradicting information
    const { data: related } = await this.supabase
      .from('brain_knowledge')
      .select('id, title, content, confidence_score')
      .eq('knowledge_type', knowledge.knowledge_type)
      .textSearch('content', this.extractKeyTerms(knowledge.content))
      .limit(10);

    if (related) {
      for (const item of related) {
        const conflict = this.analyzeConflict(knowledge, item);
        if (conflict) {
          conflicts.push({
            knowledgeId: item.id,
            type: conflict.type,
            severity: conflict.severity,
            description: conflict.description
          });
        }
      }
    }

    return conflicts;
  }

  /**
   * Validate pattern
   */
  async validatePattern(pattern) {
    const validationResult = {
      isValid: true,
      confidence: 0.5, // Start with neutral confidence
      issues: []
    };

    try {
      // Check pattern structure
      if (!pattern.conditions || !pattern.expected_outcome) {
        validationResult.isValid = false;
        validationResult.issues.push('Incomplete pattern structure');
      }

      // Check pattern occurrences
      if (pattern.occurrences < 3) {
        validationResult.confidence *= 0.5;
        validationResult.issues.push('Insufficient occurrences');
      }

      // Validate success rate
      if (pattern.success_rate) {
        if (pattern.success_rate < 50) {
          validationResult.confidence *= 0.7;
          validationResult.issues.push('Low success rate');
        } else if (pattern.success_rate > 70) {
          validationResult.confidence *= 1.3;
        }
      }

      // Check for similar patterns
      const similar = await this.findSimilarPatterns(pattern);
      if (similar.length > 0) {
        validationResult.metadata = { similarPatterns: similar };
        validationResult.confidence *= 0.8;
      }

      // Backtest if possible
      if (pattern.conditions.testable) {
        const backtestResult = await this.backtestPattern(pattern);
        validationResult.confidence *= backtestResult.confidence;
      }

      return validationResult;

    } catch (error) {
      this.handleError('Pattern validation failed', error);
      validationResult.isValid = false;
      return validationResult;
    }
  }

  /**
   * Re-validate low confidence knowledge
   */
  async revalidateLowConfidence() {
    const { data: lowConfidence } = await this.supabase
      .from('brain_knowledge')
      .select('*')
      .lt('confidence_score', 0.5)
      .eq('is_active', true)
      .limit(10);

    if (lowConfidence) {
      for (const knowledge of lowConfidence) {
        const revalidation = await this.validateKnowledge(knowledge);

        if (revalidation.confidence > knowledge.confidence_score) {
          await this.supabase
            .from('brain_knowledge')
            .update({
              confidence_score: revalidation.confidence,
              validation_status: revalidation.isValid ? 'validated' : 'rejected'
            })
            .eq('id', knowledge.id);
        }
      }
    }
  }

  /**
   * Calculate final confidence score
   */
  calculateFinalConfidence(validationResult, knowledge) {
    let confidence = validationResult.confidence;

    // Adjust based on source
    const sourceWeight = this.getSourceWeight(knowledge.source_type);
    confidence *= sourceWeight;

    // Adjust based on issues count
    const issuePenalty = Math.max(0, 1 - (validationResult.issues.length * 0.1));
    confidence *= issuePenalty;

    // Boost for well-structured content
    if (knowledge.keywords && knowledge.keywords.length > 3) {
      confidence *= 1.1;
    }

    if (knowledge.tags && knowledge.tags.length > 2) {
      confidence *= 1.05;
    }

    // Cap at 1.0
    return Math.min(1.0, confidence);
  }

  /**
   * Assess source credibility
   */
  assessSourceCredibility(sourceType) {
    const credibilityMap = {
      'manual': 1.0,
      'api': 0.95,
      'backtest': 0.9,
      'market_analysis': 0.85,
      'discovery_agent': 0.8,
      'simulation': 0.75,
      'user_interaction': 0.6,
      'external': 0.5
    };

    return credibilityMap[sourceType] || 0.5;
  }

  /**
   * Detect spam patterns
   */
  detectSpamPatterns(content) {
    const spamPatterns = [
      /\b(buy now|click here|limited time|act now)\b/gi,
      /\b(guaranteed|risk-free|100% profit)\b/gi,
      /\b(secret|exclusive|insider)\b/gi,
      /(.)\1{5,}/g, // Repeated characters
      /[A-Z]{10,}/g // Excessive caps
    ];

    for (const pattern of spamPatterns) {
      if (pattern.test(content)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Detect harmful content
   */
  detectHarmfulContent(content) {
    const harmfulPatterns = [
      /\b(scam|fraud|ponzi|rugpull)\b/gi,
      /\b(private key|seed phrase|password)\b/gi,
      /\b(illegal|laundering)\b/gi
    ];

    for (const pattern of harmfulPatterns) {
      if (pattern.test(content)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Assess information quality
   */
  async assessInformationQuality(knowledge) {
    let qualityScore = 0.7; // Start with neutral quality

    // Check for actionable information
    if (/\b(how to|steps|guide|tutorial)\b/i.test(knowledge.content)) {
      qualityScore += 0.1;
    }

    // Check for specific data/numbers
    if (/\d+(\.\d+)?%?/.test(knowledge.content)) {
      qualityScore += 0.1;
    }

    // Check for references
    if (knowledge.source_reference) {
      qualityScore += 0.1;
    }

    // Penalize vague content
    if (/\b(maybe|possibly|might|could be)\b/gi.test(knowledge.content)) {
      qualityScore -= 0.1;
    }

    // Check content depth
    const wordCount = knowledge.content.split(/\s+/).length;
    if (wordCount > 200) {
      qualityScore += 0.05;
    }
    if (wordCount < 50) {
      qualityScore -= 0.1;
    }

    return Math.max(0, Math.min(1, qualityScore));
  }

  /**
   * Generate content hash
   */
  generateContentHash(content) {
    return crypto
      .createHash('sha256')
      .update(content.toLowerCase().replace(/\s+/g, ' ').trim())
      .digest('hex');
  }

  /**
   * Load knowledge hashes for duplicate detection
   */
  async loadKnowledgeHashes() {
    const { data } = await this.supabase
      .from('brain_knowledge')
      .select('id, content_hash')
      .not('content_hash', 'is', null)
      .limit(1000);

    if (data) {
      data.forEach(item => {
        if (item.content_hash) {
          this.duplicateCache.set(item.content_hash, item.id);
        }
      });
    }
  }

  /**
   * Clean validation cache
   */
  cleanCache() {
    const maxCacheSize = 1000;
    const maxAge = 3600000; // 1 hour

    // Remove old entries
    const now = Date.now();
    for (const [key, value] of this.validationCache) {
      if (now - value.timestamp > maxAge) {
        this.validationCache.delete(key);
      }
    }

    // Limit cache size
    if (this.validationCache.size > maxCacheSize) {
      const entriesToRemove = this.validationCache.size - maxCacheSize;
      const keys = Array.from(this.validationCache.keys());
      for (let i = 0; i < entriesToRemove; i++) {
        this.validationCache.delete(keys[i]);
      }
    }
  }

  /**
   * Get validation statistics
   */
  getStatistics() {
    return {
      ...this.stats,
      approvalRate: this.stats.approved / Math.max(1, this.stats.totalValidated),
      duplicateRate: this.stats.duplicates / Math.max(1, this.stats.totalValidated),
      conflictRate: this.stats.conflicts / Math.max(1, this.stats.totalValidated)
    };
  }
}