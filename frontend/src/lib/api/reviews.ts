/**
 * API functions for reviews
 */

import { apiClient } from './client'
import type { CreateReviewRequest, ReviewResponse } from '../types/api'

export async function createReview(request: CreateReviewRequest): Promise<ReviewResponse> {
  const response = await apiClient.post<ReviewResponse>('/api/v1/reviews', request)
  return response.data
}

export async function getReview(reviewId: string): Promise<ReviewResponse> {
  const response = await apiClient.get<ReviewResponse>(`/api/v1/reviews/${reviewId}`)
  return response.data
}
