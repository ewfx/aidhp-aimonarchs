
/**
 * Adapts recommendation data from API to the format expected by the RecommendationCard component
 * This helps handle different formats between mock data and actual API responses
 * 
 * @param {Object} recommendation - The recommendation data from API
 * @returns {Object} - Formatted recommendation data
 */
export const adaptRecommendationData = (recommendation) => {
    // If recommendation is already in expected format, return as is
    if (recommendation.title && recommendation.category && recommendation.score) {
      return recommendation;
    }
  
    // Handle backend API format
    return {
      id: recommendation.recommendation_id || recommendation.id,
      title: recommendation.product_name || recommendation.name || "Product Recommendation",
      category: recommendation.product_category || recommendation.category || "Financial Product",
      score: recommendation.score || Math.floor(Math.random() * 30 + 70), // Random score between 70-99 if none provided
      reason: recommendation.reason || "This product matches your financial profile.",
      features: recommendation.features || []
    };
  };