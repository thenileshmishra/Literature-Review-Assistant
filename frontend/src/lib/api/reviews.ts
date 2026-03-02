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

export async function deleteReview(reviewId: string): Promise<void> {
  await apiClient.delete(`/api/v1/reviews/${reviewId}`)
}

export async function listReviews(limit = 50, offset = 0): Promise<ReviewResponse[]> {
  const response = await apiClient.get<ReviewResponse[]>('/api/v1/reviews', {
    params: { limit, offset },
  })
  return response.data
}
