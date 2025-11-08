import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs'

const BACKEND_URL = process.env.FASTAPI_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const { userId, getToken } = auth()
    
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const token = await getToken()
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    const backendFormData = new FormData()
    backendFormData.append('file', file)

    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: backendFormData,
    })

    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// Check status endpoint
export async function GET(request: NextRequest) {
  try {
    const { userId, getToken } = auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const token = await getToken()
    const { searchParams } = new URL(request.url)
    const jobId = searchParams.get('jobId')
    
    if (!jobId) {
      return NextResponse.json({ error: 'Job ID required' }, { status: 400 })
    }

    const response = await fetch(`${BACKEND_URL}/status/${jobId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })

    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
