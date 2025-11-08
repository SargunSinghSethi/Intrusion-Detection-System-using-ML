import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs'

const BACKEND_URL = process.env.FASTAPI_BACKEND_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  try {
    const { userId, getToken } = auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const token = await getToken()

    const response = await fetch(`${BACKEND_URL}/history`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })

    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
