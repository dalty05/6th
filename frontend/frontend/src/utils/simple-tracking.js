// src/utils/simple-tracking.js

/**
 * Lightweight referral tracking for navigation clicks
 * Tracks user behavior after clicking referral links
 */

// Generate a unique session ID
function getSessionId() {
  let sessionId = sessionStorage.getItem('referral_session_id')
  if (!sessionId) {
    sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    sessionStorage.setItem('referral_session_id', sessionId)
  }
  return sessionId
}

// Get screen size
function getScreenSize() {
  return `${window.innerWidth}x${window.innerHeight}`
}

export function initReferralTracking() {
  // Check if user came from a referral link
  const urlParams = new URLSearchParams(window.location.search)
  const referralCode = urlParams.get('ref')
  
  // Also check cookies (set when referral link was clicked)
  const cookieReferral = document.cookie.split('; ').find(row => row.startsWith('referral_code='))
  const finalReferralCode = referralCode || (cookieReferral ? cookieReferral.split('=')[1] : null)
  
  if (!finalReferralCode) {
  
    return
  }

  // Set cookie if not already set
  if (!cookieReferral) {
    document.cookie = `referral_code=${finalReferralCode}; path=/; max-age=${60*60*24*30}`
  }

  const sessionId = getSessionId()
  const startTime = Date.now()
  
  console.log('📊 Referral tracking active:', {
    code: finalReferralCode,
    sessionId: sessionId
  })

  // Track page view
  trackAction({
    referralCode: finalReferralCode,
    sessionId: sessionId,
    action: 'page_view',
    pageUrl: window.location.href,
    pageTitle: document.title,
    referrerUrl: document.referrer,
    screenSize: getScreenSize()
  })

  // Track all navigation clicks
  document.addEventListener('click', function trackNavigation(e) {
    // Find the closest link element
    const link = e.target.closest('a')
    
    // Only track if it's a link
    if (!link) return
    
    // Skip if it's an external link or has no href
    if (!link.href || link.href.startsWith('javascript:')) return
    
    // Skip if it's a hash link (same page navigation)
    if (link.href === window.location.href || link.href === window.location.href + '#') return

    // Prepare tracking data
    const trackingData = {
      referralCode: finalReferralCode,
      sessionId: sessionId,
      action: 'nav_click',
      linkText: link.textContent?.trim() || 'Link',
      linkHref: link.href,
      linkId: link.id || null,
      linkClass: link.className || null,
      pageUrl: window.location.href,
      pageTitle: document.title,
      referrerUrl: document.referrer,
      screenSize: getScreenSize(),
      timeSpent: Math.floor((Date.now() - startTime) / 1000)
    }

    console.log('📊 Referral navigation tracked:', trackingData.linkText)

    // Send to backend
    sendTrackingData(trackingData)
  })

  // Track when user leaves the page
  window.addEventListener('beforeunload', function() {
    const timeSpent = Math.floor((Date.now() - startTime) / 1000)
    
    // Only track if they spent more than 3 seconds
    if (timeSpent > 3) {
      const exitData = {
        referralCode: finalReferralCode,
        sessionId: sessionId,
        action: 'exit',
        timeSpent: timeSpent,
        pageUrl: window.location.href,
        pageTitle: document.title,
        screenSize: getScreenSize()
      }
      
      console.log('📊 User exit tracked:', timeSpent + 's')
      
      // Use sendBeacon for reliable exit tracking
      if (navigator.sendBeacon) {
        navigator.sendBeacon(
          '/api/referral/track-nav',
          JSON.stringify(exitData)
        )
      } else {
        // Fallback to fetch
        sendTrackingData(exitData)
      }
    }
  })

  // Track scroll depth (simple version)
  let maxScrollDepth = 0
  window.addEventListener('scroll', function() {
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
    const scrolled = window.scrollY
    const percentage = Math.round((scrolled / scrollHeight) * 100)
    
    // Only track at thresholds
    if (percentage >= 25 && maxScrollDepth < 25) {
      maxScrollDepth = 25
      trackAction({
        referralCode: finalReferralCode,
        sessionId: sessionId,
        action: 'scroll',
        linkText: 'Scroll 25%',
        pageUrl: window.location.href,
        pageTitle: document.title,
        screenSize: getScreenSize()
      })
    } else if (percentage >= 50 && maxScrollDepth < 50) {
      maxScrollDepth = 50
      trackAction({
        referralCode: finalReferralCode,
        sessionId: sessionId,
        action: 'scroll',
        linkText: 'Scroll 50%',
        pageUrl: window.location.href,
        pageTitle: document.title,
        screenSize: getScreenSize()
      })
    } else if (percentage >= 75 && maxScrollDepth < 75) {
      maxScrollDepth = 75
      trackAction({
        referralCode: finalReferralCode,
        sessionId: sessionId,
        action: 'scroll',
        linkText: 'Scroll 75%',
        pageUrl: window.location.href,
        pageTitle: document.title,
        screenSize: getScreenSize()
      })
    } else if (percentage >= 100 && maxScrollDepth < 100) {
      maxScrollDepth = 100
      trackAction({
        referralCode: finalReferralCode,
        sessionId: sessionId,
        action: 'scroll',
        linkText: 'Scroll 100%',
        pageUrl: window.location.href,
        pageTitle: document.title,
        screenSize: getScreenSize()
      })
    }
  })
}

// Track an action
function trackAction(data) {
  sendTrackingData(data)
}

// Send tracking data to backend
async function sendTrackingData(data) {
  try {
    const response = await fetch('/api/referral/track-nav', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })
    
    if (!response.ok) {
      console.warn('⚠️ Failed to send tracking data:', response.status)
    }
  } catch (error) {
    // Silently fail - don't break user experience
    console.warn('⚠️ Tracking error:', error.message)
  }
}