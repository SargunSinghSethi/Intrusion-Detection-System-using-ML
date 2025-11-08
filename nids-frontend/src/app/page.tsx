'use client'

import { SignInButton, SignUpButton, useUser } from '@clerk/nextjs'
import { Shield, Activity, AlertTriangle, BarChart3, ArrowRight, Mail, Phone, MapPin } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function HomePage() {
  const { isSignedIn } = useUser()

  if (isSignedIn) {
    return <DashboardRedirect />
  }

  return (
    <div className="min-h-screen gradient-bg">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">NIDS</span>
            </div>
            <div className="flex items-center space-x-4">
              <SignInButton mode="modal">
                <button className="btn-secondary">Login</button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="btn-primary">Sign Up</button>
              </SignUpButton>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 leading-tight">
              Network Intrusion
              <span className="block text-primary-600">Detection System</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Advanced AI-powered threat detection and real-time network monitoring 
              to protect your infrastructure from cyber attacks and malicious activities.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <SignUpButton mode="modal">
                <button className="btn-primary text-lg px-8 py-3 flex items-center space-x-2">
                  <span>Get Started</span>
                  <ArrowRight className="h-5 w-5" />
                </button>
              </SignUpButton>
              <SignInButton mode="modal">
                <button className="btn-secondary text-lg px-8 py-3">
                  Learn More
                </button>
              </SignInButton>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Why Choose NIDS?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our cutting-edge technology provides comprehensive protection against 
              evolving cyber threats with real-time analysis and instant alerts.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card text-center hover:shadow-xl transition-shadow duration-300"
              >
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="grid md:grid-cols-3 gap-8 text-center"
          >
            {stats.map((stat, index) => (
              <div key={index} className="space-y-2">
                <div className="text-4xl md:text-5xl font-bold text-primary-600">
                  {stat.value}
                </div>
                <div className="text-lg text-gray-600">
                  {stat.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-primary-400" />
                <span className="text-2xl font-bold">NIDS</span>
              </div>
              <p className="text-gray-400">
                Advanced Network Intrusion Detection System for comprehensive 
                cybersecurity protection.
              </p>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Contact Us</h3>
              <div className="space-y-2 text-gray-400">
                <div className="flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>nis@nids.com</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Phone className="h-4 w-4" />
                  <span>+1 (555) 123-4567</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>123 Security St, Tech City</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Real-time Monitoring</li>
                <li>Threat Detection</li>
                <li>Incident Response</li>
                <li>Analytics Dashboard</li>
              </ul>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Documentation</li>
                <li>API Reference</li>
                <li>Community Forum</li>
                <li>24/7 Support</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2024 NIDS. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function DashboardRedirect() {
  return (
    <div className="min-h-screen flex items-center justify-center gradient-bg">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-6"
      >
        <Shield className="h-16 w-16 text-primary-600 mx-auto" />
        <h1 className="text-3xl font-bold text-gray-900">Welcome to NIDS</h1>
        <p className="text-gray-600">Redirecting to dashboard...</p>
        <Link href="/dashboard" className="btn-primary">
          Go to Dashboard
        </Link>
      </motion.div>
    </div>
  )
}

const features = [
  {
    icon: Activity,
    title: 'Real-time Monitoring',
    description: 'Continuous network traffic analysis with instant threat detection and alerting.'
  },
  {
    icon: AlertTriangle,
    title: 'Threat Detection',
    description: 'Advanced AI algorithms identify malicious patterns and suspicious activities.'
  },
  {
    icon: BarChart3,
    title: 'Analytics Dashboard',
    description: 'Comprehensive insights and reports on network security status and trends.'
  },
  {
    icon: Shield,
    title: 'Incident Response',
    description: 'Automated response mechanisms to mitigate threats and protect your network.'
  }
]

const stats = [
  { value: '99.9%', label: 'Detection Accuracy' },
  { value: '< 1ms', label: 'Response Time' },
  { value: '24/7', label: 'Monitoring' }
]

