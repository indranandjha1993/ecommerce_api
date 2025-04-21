import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { useAuth } from '../../hooks/useAuth';
import { addNotification } from '../../store/slices/uiSlice';
import { formatDate } from '../../utils/formatters';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';
import { api } from '../../services/api';

interface Review {
  id: string;
  user: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  rating: number;
  title: string;
  content: string;
  created_at: string;
}

interface ProductReviewsProps {
  productId: string;
}

const ProductReviews: React.FC<ProductReviewsProps> = ({ productId }) => {
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useAuth();
  
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [userReview, setUserReview] = useState<Review | null>(null);
  const [submitting, setSubmitting] = useState(false);
  
  // Form state
  const [rating, setRating] = useState(5);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  
  // Fetch reviews
  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/products/${productId}/reviews`);
        setReviews(response.data.items || []);
        
        // Check if the user has already submitted a review
        if (isAuthenticated && user) {
          const userReview = response.data.items.find(
            (review: Review) => review.user.id === user.id
          );
          if (userReview) {
            setUserReview(userReview);
            // Pre-fill form if user wants to edit
            setRating(userReview.rating);
            setTitle(userReview.title);
            setContent(userReview.content);
          }
        }
        
        setError(null);
      } catch (err) {
        setError('Failed to load reviews. Please try again later.');
        console.error('Error fetching reviews:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchReviews();
  }, [productId, isAuthenticated, user]);
  
  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'You must be logged in to submit a review.',
        })
      );
      return;
    }
    
    try {
      setSubmitting(true);
      
      const reviewData = {
        rating,
        title,
        content,
      };
      
      let response;
      
      if (userReview) {
        // Update existing review
        response = await api.put(`/products/${productId}/reviews/${userReview.id}`, reviewData);
      } else {
        // Create new review
        response = await api.post(`/products/${productId}/reviews`, reviewData);
      }
      
      // Update reviews list
      if (userReview) {
        setReviews(
          reviews.map((review) =>
            review.id === userReview.id ? response.data : review
          )
        );
        setUserReview(response.data);
      } else {
        setReviews([response.data, ...reviews]);
        setUserReview(response.data);
      }
      
      setShowReviewForm(false);
      
      dispatch(
        addNotification({
          type: 'success',
          message: userReview
            ? 'Your review has been updated!'
            : 'Your review has been submitted!',
        })
      );
    } catch (err) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to submit review. Please try again.',
        })
      );
      console.error('Error submitting review:', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleDeleteReview = async () => {
    if (!userReview) return;
    
    try {
      setSubmitting(true);
      await api.delete(`/products/${productId}/reviews/${userReview.id}`);
      
      // Remove from reviews list
      setReviews(reviews.filter((review) => review.id !== userReview.id));
      setUserReview(null);
      
      // Reset form
      setRating(5);
      setTitle('');
      setContent('');
      
      dispatch(
        addNotification({
          type: 'success',
          message: 'Your review has been deleted.',
        })
      );
    } catch (err) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to delete review. Please try again.',
        })
      );
      console.error('Error deleting review:', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4">
        <div className="flex">
          <svg
            className="h-5 w-5 text-red-400 mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div>
      {/* Review form toggle */}
      {isAuthenticated && (
        <div className="mb-8">
          {!showReviewForm ? (
            <Button
              variant="primary"
              onClick={() => setShowReviewForm(true)}
            >
              {userReview ? 'Edit Your Review' : 'Write a Review'}
            </Button>
          ) : (
            <Button
              variant="outline"
              onClick={() => setShowReviewForm(false)}
            >
              Cancel
            </Button>
          )}
        </div>
      )}
      
      {/* Review form */}
      {showReviewForm && (
        <div className="bg-gray-50 p-6 rounded-lg mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {userReview ? 'Edit Your Review' : 'Write a Review'}
          </h3>
          <form onSubmit={handleSubmitReview}>
            {/* Rating */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating
              </label>
              <div className="flex items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    className="focus:outline-none"
                    onClick={() => setRating(star)}
                  >
                    <svg
                      className={`h-8 w-8 ${
                        star <= rating ? 'text-yellow-400' : 'text-gray-300'
                      }`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </button>
                ))}
                <span className="ml-2 text-sm text-gray-500">
                  {rating} out of 5 stars
                </span>
              </div>
            </div>
            
            {/* Title */}
            <div className="mb-4">
              <label htmlFor="review-title" className="block text-sm font-medium text-gray-700 mb-2">
                Review Title
              </label>
              <input
                type="text"
                id="review-title"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            
            {/* Content */}
            <div className="mb-4">
              <label htmlFor="review-content" className="block text-sm font-medium text-gray-700 mb-2">
                Review Content
              </label>
              <textarea
                id="review-content"
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
              />
            </div>
            
            {/* Submit buttons */}
            <div className="flex space-x-4">
              <Button
                type="submit"
                variant="primary"
                isLoading={submitting}
                disabled={submitting}
              >
                {userReview ? 'Update Review' : 'Submit Review'}
              </Button>
              
              {userReview && (
                <Button
                  type="button"
                  variant="danger"
                  onClick={handleDeleteReview}
                  isLoading={submitting}
                  disabled={submitting}
                >
                  Delete Review
                </Button>
              )}
            </div>
          </form>
        </div>
      )}
      
      {/* Reviews list */}
      {reviews.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">
            No reviews yet. Be the first to review this product!
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {reviews.map((review) => (
            <div key={review.id} className="border-b border-gray-200 pb-6">
              <div className="flex items-center mb-2">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm">
                  {review.user.first_name?.[0]?.toUpperCase() || review.user.email?.[0]?.toUpperCase() || '?'}
                </div>
                <div className="ml-4">
                  <h4 className="text-sm font-medium text-gray-900">
                    {review.user.first_name
                      ? `${review.user.first_name} ${review.user.last_name || ''}`
                      : 'Anonymous'}
                  </h4>
                  <div className="flex items-center">
                    <div className="flex text-yellow-400">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <svg
                          key={star}
                          className={`h-4 w-4 ${
                            star <= review.rating ? 'text-yellow-400' : 'text-gray-300'
                          }`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    <span className="ml-2 text-xs text-gray-500">
                      {formatDate(review.created_at)}
                    </span>
                  </div>
                </div>
              </div>
              <h3 className="text-base font-medium text-gray-900 mt-4 mb-2">
                {review.title}
              </h3>
              <p className="text-gray-600">{review.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductReviews;