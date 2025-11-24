/**
 * Response Formatter Utility
 * Standardizes API responses across all endpoints
 */

class ResponseFormatter {
  /**
   * Success response
   */
  static success(data, message = null) {
    const response = {
      success: true,
      data
    };
    
    if (message) {
      response.message = message;
    }
    
    return response;
  }

  /**
   * Error response
   */
  static error(error, statusCode = 500) {
    return {
      success: false,
      error: typeof error === 'string' ? error : error.message,
      statusCode
    };
  }

  /**
   * Paginated response
   */
  static paginated(data, page, limit, total) {
    return {
      success: true,
      data,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    };
  }
}

module.exports = ResponseFormatter;
