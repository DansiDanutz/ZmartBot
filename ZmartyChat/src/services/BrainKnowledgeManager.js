/**
 * ZMARTY BRAIN KNOWLEDGE MANAGER
 * Central service for managing all knowledge operations
 * Handles storage, retrieval, learning, and evolution
 */

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { marked } from 'marked';
import TurndownService from 'turndown';
import config from '../config/secure-config.js';
import { aiProviderService } from './AIProviderService.js';

class BrainKnowledgeManager {
  constructor() {
    // Initialize Supabase client with secure config
    this.supabase = createClient(
      config.supabase.url,
      config.supabase.anonKey
    );

    // Use the unified AI Provider Service
    this.aiProvider = aiProviderService;

    // Markdown converter
    this.turndown = new TurndownService();

    // Cache layers
    this.memoryCache = new Map(); // In-memory cache
    this.categoryCache = new Map();
    this.patternCache = new Map();

    // Performance tracking
    this.metrics = {
      queries: 0,
      cacheHits: 0,
      apiCalls: 0,
      avgResponseTime: 0
    };

    // Initialize categories and ensure database is ready
    this.initialize();
  }

  async initialize() {
    try {
      console.log('🧠 Initializing Brain Knowledge Manager...');

      // Load categories into cache
      await this.loadCategories();

      // Warm up frequently accessed knowledge
      await this.warmupCache();

      // Start maintenance tasks
      this.startMaintenanceTasks();

      console.log('✅ Brain Knowledge Manager initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Brain Knowledge Manager:', error);
    }
  }

  // ========================================
  // KNOWLEDGE OPERATIONS
  // ========================================

  /**
   * Store new knowledge in the brain
   */
  async storeKnowledge({
    title,
    content,
    category,
    type,
    source,
    keywords = [],
    tags = [],
    metadata = {}
  }) {
    try {
      const startTime = Date.now();

      // Find or create category
      const categoryId = await this.getCategoryId(category);

      // Generate slug
      const slug = this.generateSlug(title);

      // Generate embeddings for semantic search
      const embedding = await this.generateEmbedding(content);

      // Prepare content in multiple formats
      const contentMd = content;
      const contentHtml = marked(content);
      const summary = await this.generateSummary(content);

      // Store in database
      const { data, error } = await this.supabase
        .from('brain_knowledge')
        .insert({
          category_id: categoryId,
          title,
          slug,
          content,
          content_md: contentMd,
          content_html: contentHtml,
          summary,
          knowledge_type: type,
          source_type: source,
          source_timestamp: new Date().toISOString(),
          keywords,
          tags,
          embedding,
          metadata,
          confidence_score: this.calculateInitialConfidence(source)
        })
        .select()
        .single();

      if (error) throw error;

      // Update cache
      this.memoryCache.set(data.id, data);

      // Generate MD file
      await this.generateMDFile(data);

      // Track performance
      this.updateMetrics('store', Date.now() - startTime);

      console.log(`✅ Stored knowledge: ${title} (${data.id})`);
      return data;

    } catch (error) {
      console.error('❌ Failed to store knowledge:', error);
      throw error;
    }
  }

  /**
   * Retrieve knowledge with intelligent fallback
   */
  async retrieveKnowledge(query, options = {}) {
    try {
      const startTime = Date.now();
      this.metrics.queries++;

      // Level 1: Memory cache
      const cacheKey = this.generateCacheKey(query, options);
      if (this.memoryCache.has(cacheKey)) {
        this.metrics.cacheHits++;
        this.updateMetrics('retrieve', Date.now() - startTime);
        return this.memoryCache.get(cacheKey);
      }

      // Level 2: Exact match search
      let result = await this.searchExactMatch(query);
      if (result) {
        this.memoryCache.set(cacheKey, result);
        this.updateMetrics('retrieve', Date.now() - startTime);
        return result;
      }

      // Level 3: Fuzzy search
      result = await this.searchFuzzy(query, options.threshold || 0.7);
      if (result) {
        this.memoryCache.set(cacheKey, result);
        this.updateMetrics('retrieve', Date.now() - startTime);
        return result;
      }

      // Level 4: Semantic search
      result = await this.searchSemantic(query, options.limit || 5);
      if (result && result.length > 0) {
        this.memoryCache.set(cacheKey, result);
        this.updateMetrics('retrieve', Date.now() - startTime);
        return result;
      }

      // Level 5: API fallback
      if (options.allowAPI) {
        result = await this.fetchFromAPI(query);
        if (result) {
          // Store for future use
          await this.storeKnowledge({
            title: `API Response: ${query}`,
            content: result,
            category: 'api-cache',
            type: 'api_cache',
            source: 'api',
            metadata: { query, timestamp: Date.now() }
          });
          this.metrics.apiCalls++;
        }
      }

      this.updateMetrics('retrieve', Date.now() - startTime);
      return result || null;

    } catch (error) {
      console.error('❌ Failed to retrieve knowledge:', error);
      return null;
    }
  }

  /**
   * Search for exact matches
   */
  async searchExactMatch(query) {
    const { data } = await this.supabase
      .from('brain_knowledge')
      .select('*')
      .or(`title.ilike.%${query}%,keywords.cs.{${query}}`)
      .eq('is_active', true)
      .order('usage_count', { ascending: false })
      .limit(1)
      .single();

    if (data) {
      await this.incrementUsage(data.id);
    }

    return data;
  }

  /**
   * Fuzzy search implementation
   */
  async searchFuzzy(query, threshold = 0.7) {
    const { data } = await this.supabase
      .from('brain_knowledge')
      .select('*, similarity:title.distance(query)')
      .textSearch('content', query)
      .eq('is_active', true)
      .gte('confidence_score', threshold)
      .order('usage_count', { ascending: false })
      .limit(10);

    return data;
  }

  /**
   * Semantic search using embeddings
   */
  async searchSemantic(query, limit = 5) {
    const queryEmbedding = await this.generateEmbedding(query);

    const { data } = await this.supabase.rpc('find_similar_knowledge', {
      search_embedding: queryEmbedding,
      limit_count: limit
    });

    return data;
  }

  // ========================================
  // LEARNING & EVOLUTION
  // ========================================

  /**
   * Learn from user interaction
   */
  async learnFromInteraction({
    userId,
    question,
    answer,
    source,
    wasHelpful,
    context = {}
  }) {
    try {
      // Store interaction
      const { data: interaction } = await this.supabase
        .from('brain_user_interactions')
        .insert({
          user_id: userId,
          interaction_type: 'query',
          question,
          answer,
          answer_source: source,
          was_helpful: wasHelpful,
          context,
          response_time: context.responseTime
        })
        .select()
        .single();

      // Update user memory profile
      await this.updateUserMemory(userId, interaction);

      // Queue for learning if significant
      if (wasHelpful || context.newPattern) {
        await this.queueForLearning({
          type: 'user_feedback',
          content: { question, answer, context },
          source: `user_${userId}`,
          priority: wasHelpful ? 7 : 3
        });
      }

      // Discover patterns
      await this.discoverPatterns(interaction);

    } catch (error) {
      console.error('❌ Failed to learn from interaction:', error);
    }
  }

  /**
   * Discover patterns from interactions
   */
  async discoverPatterns(interaction) {
    // Check if this interaction reveals a pattern
    const similarInteractions = await this.findSimilarInteractions(interaction);

    if (similarInteractions.length >= 3) {
      // Pattern detected
      const pattern = this.extractPattern(similarInteractions);

      if (pattern) {
        await this.storePattern(pattern);
      }
    }
  }

  /**
   * Store discovered pattern
   */
  async storePattern(pattern) {
    const { data, error } = await this.supabase
      .from('brain_patterns')
      .insert({
        pattern_name: pattern.name,
        pattern_type: pattern.type,
        description: pattern.description,
        conditions: pattern.conditions,
        expected_outcome: pattern.outcome,
        confidence_level: pattern.confidence,
        discovered_by: 'discovery_agent'
      })
      .select()
      .single();

    if (data) {
      console.log(`🔍 New pattern discovered: ${pattern.name}`);
      this.patternCache.set(data.id, data);

      // Create knowledge entry for the pattern
      await this.storeKnowledge({
        title: `Pattern: ${pattern.name}`,
        content: this.generatePatternDocumentation(pattern),
        category: 'discoveries',
        type: 'pattern',
        source: 'discovery_agent',
        tags: ['pattern', pattern.type]
      });
    }
  }

  // ========================================
  // CATEGORY MANAGEMENT
  // ========================================

  /**
   * Load categories into cache
   */
  async loadCategories() {
    const { data } = await this.supabase
      .from('brain_categories')
      .select('*')
      .eq('is_active', true)
      .order('level', { ascending: true })
      .order('priority', { ascending: false });

    if (data) {
      data.forEach(category => {
        this.categoryCache.set(category.slug, category);
      });
    }
  }

  /**
   * Get category ID by slug or create new
   */
  async getCategoryId(categorySlug) {
    // Check cache
    if (this.categoryCache.has(categorySlug)) {
      return this.categoryCache.get(categorySlug).id;
    }

    // Check database
    const { data: existing } = await this.supabase
      .from('brain_categories')
      .select('id')
      .eq('slug', categorySlug)
      .single();

    if (existing) {
      return existing.id;
    }

    // Create new category
    const { data: newCategory } = await this.supabase
      .from('brain_categories')
      .insert({
        name: this.slugToTitle(categorySlug),
        slug: categorySlug,
        description: `Auto-created category for ${categorySlug}`
      })
      .select()
      .single();

    if (newCategory) {
      this.categoryCache.set(categorySlug, newCategory);
      return newCategory.id;
    }

    return null;
  }

  // ========================================
  // MD FILE GENERATION
  // ========================================

  /**
   * Generate MD file for knowledge
   */
  async generateMDFile(knowledge) {
    try {
      const category = this.categoryCache.get(knowledge.category_id) || { path: 'uncategorized' };
      const dirPath = path.join(
        process.env.BRAIN_MD_PATH || './docs/BRAIN',
        category.path
      );

      // Ensure directory exists
      await fs.mkdir(dirPath, { recursive: true });

      // Generate MD content
      const mdContent = this.generateMDContent(knowledge);

      // Write file
      const filePath = path.join(dirPath, `${knowledge.slug}.md`);
      await fs.writeFile(filePath, mdContent);

      console.log(`📄 Generated MD file: ${filePath}`);

    } catch (error) {
      console.error('❌ Failed to generate MD file:', error);
    }
  }

  /**
   * Generate MD content for knowledge
   */
  generateMDContent(knowledge) {
    const category = this.categoryCache.get(knowledge.category_id) || { name: 'Unknown' };

    return `# ${knowledge.title}

## Metadata
- **ID**: ${knowledge.id}
- **Category**: ${category.name}
- **Type**: ${knowledge.knowledge_type}
- **Confidence**: ${(knowledge.confidence_score * 100).toFixed(1)}%
- **Created**: ${new Date(knowledge.created_at).toLocaleDateString()}
- **Last Updated**: ${new Date(knowledge.updated_at).toLocaleDateString()}
- **Usage Count**: ${knowledge.usage_count}

## Summary
${knowledge.summary || 'No summary available'}

## Content
${knowledge.content}

## Keywords
${knowledge.keywords.map(k => `- ${k}`).join('\n')}

## Tags
${knowledge.tags.map(t => `#${t}`).join(' ')}

## Related Knowledge
${knowledge.related_knowledge_ids?.map(id => `- [${id}](${id}.md)`).join('\n') || 'None'}

## Source
- **Type**: ${knowledge.source_type}
- **Reference**: ${knowledge.source_reference || 'N/A'}
- **Timestamp**: ${knowledge.source_timestamp}

## Performance Metrics
- **Success Rate**: ${knowledge.success_count}/${knowledge.success_count + knowledge.failure_count}
- **Average Response Time**: ${knowledge.avg_response_time}ms
- **Last Accessed**: ${knowledge.last_accessed || 'Never'}

---
*This knowledge is part of Zmarty's Brain Management System*
`;
  }

  // ========================================
  // CACHING & PERFORMANCE
  // ========================================

  /**
   * Warm up cache with frequently accessed knowledge
   */
  async warmupCache() {
    const { data } = await this.supabase
      .from('brain_knowledge')
      .select('*')
      .eq('is_active', true)
      .order('usage_count', { ascending: false })
      .limit(100);

    if (data) {
      data.forEach(item => {
        this.memoryCache.set(item.id, item);
      });
      console.log(`🔥 Warmed up cache with ${data.length} items`);
    }
  }

  /**
   * Cache API response
   */
  async cacheAPIResponse(query, response, ttlSeconds = 3600) {
    const cacheKey = this.generateCacheKey(query);
    const queryHash = crypto.createHash('sha256').update(query).digest('hex');

    const { data } = await this.supabase
      .from('brain_api_cache')
      .upsert({
        cache_key: cacheKey,
        query_hash: queryHash,
        response_data: response,
        response_text: JSON.stringify(response),
        ttl_seconds: ttlSeconds,
        expires_at: new Date(Date.now() + ttlSeconds * 1000).toISOString()
      })
      .select()
      .single();

    return data;
  }

  // ========================================
  // USER MEMORY MANAGEMENT
  // ========================================

  /**
   * Update user memory profile
   */
  async updateUserMemory(userId, interaction) {
    try {
      // Get existing profile or create new
      const { data: profile } = await this.supabase
        .from('brain_user_memory')
        .select('*')
        .eq('user_id', userId)
        .single();

      if (profile) {
        // Update existing profile
        const updates = {
          total_interactions: profile.total_interactions + 1,
          last_active: new Date().toISOString()
        };

        // Update common questions
        const questions = profile.common_questions || {};
        const questionCategory = this.categorizeQuestion(interaction.question);
        questions[questionCategory] = (questions[questionCategory] || 0) + 1;
        updates.common_questions = questions;

        await this.supabase
          .from('brain_user_memory')
          .update(updates)
          .eq('user_id', userId);

      } else {
        // Create new profile
        await this.supabase
          .from('brain_user_memory')
          .insert({
            user_id: userId,
            total_interactions: 1,
            common_questions: { [this.categorizeQuestion(interaction.question)]: 1 },
            last_active: new Date().toISOString()
          });
      }

    } catch (error) {
      console.error('❌ Failed to update user memory:', error);
    }
  }

  // ========================================
  // MAINTENANCE & OPTIMIZATION
  // ========================================

  /**
   * Start background maintenance tasks
   */
  startMaintenanceTasks() {
    // Clean expired cache every hour
    setInterval(() => this.cleanExpiredCache(), 3600000);

    // Update confidence scores every 6 hours
    setInterval(() => this.updateConfidenceScores(), 21600000);

    // Generate daily report
    setInterval(() => this.generateDailyReport(), 86400000);

    // Optimize indexes every week
    setInterval(() => this.optimizeIndexes(), 604800000);
  }

  /**
   * Clean expired cache entries
   */
  async cleanExpiredCache() {
    const { data } = await this.supabase.rpc('clean_expired_cache');
    console.log(`🧹 Cleaned ${data} expired cache entries`);
  }

  /**
   * Update knowledge confidence scores
   */
  async updateConfidenceScores() {
    const { data: knowledge } = await this.supabase
      .from('brain_knowledge')
      .select('id, usage_count, success_count, failure_count, created_at')
      .eq('is_active', true);

    for (const item of knowledge) {
      const daysOld = Math.floor((Date.now() - new Date(item.created_at).getTime()) / 86400000);
      const confidence = await this.supabase.rpc('calculate_knowledge_confidence', {
        p_usage_count: item.usage_count,
        p_success_count: item.success_count,
        p_failure_count: item.failure_count,
        p_days_old: daysOld
      });

      await this.supabase
        .from('brain_knowledge')
        .update({ confidence_score: confidence })
        .eq('id', item.id);
    }

    console.log(`📊 Updated confidence scores for ${knowledge.length} items`);
  }

  // ========================================
  // UTILITY FUNCTIONS
  // ========================================

  /**
   * Generate embedding for text
   */
  async generateEmbedding(text) {
    try {
      const response = await this.openai.embeddings.create({
        model: 'text-embedding-3-small',
        input: text.substring(0, 8000) // Limit text length
      });
      return response.data[0].embedding;
    } catch (error) {
      console.error('Failed to generate embedding:', error);
      return null;
    }
  }

  /**
   * Generate summary of content
   */
  async generateSummary(content) {
    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [{
          role: 'system',
          content: 'Summarize this trading/crypto content in 2-3 sentences'
        }, {
          role: 'user',
          content: content.substring(0, 3000)
        }],
        max_tokens: 100,
        temperature: 0.3
      });
      return response.choices[0].message.content;
    } catch (error) {
      return content.substring(0, 200) + '...';
    }
  }

  /**
   * Generate slug from title
   */
  generateSlug(title) {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  /**
   * Generate cache key
   */
  generateCacheKey(query, options = {}) {
    return crypto
      .createHash('md5')
      .update(JSON.stringify({ query, ...options }))
      .digest('hex');
  }

  /**
   * Convert slug to title
   */
  slugToTitle(slug) {
    return slug
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Categorize question type
   */
  categorizeQuestion(question) {
    const lower = question.toLowerCase();
    if (lower.includes('price') || lower.includes('how much')) return 'price';
    if (lower.includes('buy') || lower.includes('sell')) return 'trading';
    if (lower.includes('risk')) return 'risk';
    if (lower.includes('indicator') || lower.includes('rsi') || lower.includes('macd')) return 'technical';
    if (lower.includes('strategy')) return 'strategy';
    return 'general';
  }

  /**
   * Calculate initial confidence based on source
   */
  calculateInitialConfidence(source) {
    const confidenceMap = {
      'manual': 1.0,
      'api': 0.9,
      'discovery_agent': 0.7,
      'user_interaction': 0.6,
      'market_analysis': 0.8,
      'backtest': 0.85,
      'simulation': 0.75,
      'external': 0.5
    };
    return confidenceMap[source] || 0.5;
  }

  /**
   * Increment usage count for knowledge
   */
  async incrementUsage(knowledgeId) {
    await this.supabase.rpc('increment_knowledge_usage', {
      knowledge_uuid: knowledgeId
    });
  }

  /**
   * Update performance metrics
   */
  updateMetrics(operation, duration) {
    const alpha = 0.1; // Exponential moving average factor
    this.metrics.avgResponseTime =
      alpha * duration + (1 - alpha) * this.metrics.avgResponseTime;
  }

  /**
   * Generate daily brain report
   */
  async generateDailyReport() {
    const report = {
      date: new Date().toISOString(),
      metrics: this.metrics,
      cache_hit_rate: (this.metrics.cacheHits / this.metrics.queries * 100).toFixed(2) + '%',
      api_call_rate: (this.metrics.apiCalls / this.metrics.queries * 100).toFixed(2) + '%'
    };

    // Get knowledge stats
    const { count: knowledgeCount } = await this.supabase
      .from('brain_knowledge')
      .select('*', { count: 'exact', head: true })
      .eq('is_active', true);

    const { count: patternCount } = await this.supabase
      .from('brain_patterns')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'active');

    report.knowledge_items = knowledgeCount;
    report.active_patterns = patternCount;

    console.log('📊 Daily Brain Report:', report);

    // Store report
    await this.supabase
      .from('brain_evolution_log')
      .insert({
        evolution_type: 'daily_report',
        description: 'Daily brain performance report',
        metrics_after: report
      });

    return report;
  }
}

// Export singleton instance
const brainManager = new BrainKnowledgeManager();
export default brainManager;