# Global Coverage Analysis

## 🌍 Target Markets

Your IELTS preparation platform serves students globally:
- **South Asia:** India, Pakistan, Bangladesh
- **Middle East & Africa:** UAE, Saudi Arabia, Egypt, Nigeria, South Africa
- **East Asia:** Hong Kong, South Korea, Japan
- **Oceania:** Australia, New Zealand
- **Europe:** UK, Ireland, Germany, France
- **Americas:** Canada, Mexico, Brazil, Argentina, Chile

---

## 📍 Selected Cloud Run Regions (6 Regions)

### **Primary Region**
**asia-south1 (Mumbai, India)**
- **Serves:** India, Pakistan, Bangladesh, Middle East
- **Latency:**
  - India: 10-30ms
  - Pakistan: 40-60ms
  - Bangladesh: 50-70ms
  - Dubai/UAE: 60-80ms
  - Saudi Arabia: 70-90ms

### **Secondary Regions**

**1. europe-west2 (London, UK)**
- **Serves:** UK, Europe, North & West Africa
- **Latency:**
  - UK: 5-15ms
  - Ireland: 15-25ms
  - France/Germany: 20-40ms
  - Nigeria: 80-100ms
  - Egypt: 50-70ms

**2. asia-northeast1 (Tokyo, Japan)**
- **Serves:** Japan, South Korea, Hong Kong
- **Latency:**
  - Japan: 5-15ms
  - South Korea: 30-50ms
  - Hong Kong: 50-70ms
  - Taiwan: 60-80ms

**3. australia-southeast1 (Sydney, Australia)**
- **Serves:** Australia, New Zealand, Pacific Islands
- **Latency:**
  - Sydney: 5-15ms
  - Melbourne: 15-25ms
  - New Zealand: 30-50ms
  - Brisbane: 10-20ms

**4. southamerica-east1 (São Paulo, Brazil)**
- **Serves:** Brazil, Argentina, Chile, South America
- **Latency:**
  - São Paulo: 5-15ms
  - Rio de Janeiro: 15-25ms
  - Buenos Aires: 40-60ms
  - Santiago: 60-80ms

**5. northamerica-northeast1 (Montreal, Canada)**
- **Serves:** Canada, Mexico, Northeast USA
- **Latency:**
  - Toronto: 15-25ms
  - Montreal: 5-15ms
  - Mexico City: 60-80ms
  - New York: 20-30ms

---

## ✅ Coverage Summary

| **Region** | **Cloud Run Location** | **Typical Latency** |
|-----------|------------------------|---------------------|
| India | Mumbai | 10-30ms ✅ |
| Pakistan | Mumbai | 40-60ms ✅ |
| Bangladesh | Mumbai | 50-70ms ✅ |
| UAE/Middle East | Mumbai | 60-90ms ✅ |
| Saudi Arabia | Mumbai | 70-90ms ✅ |
| Nigeria | London | 80-100ms ✅ |
| Egypt | London | 50-70ms ✅ |
| South Africa | London | 120-150ms ⚠️ |
| UK | London | 5-15ms ✅ |
| Europe | London | 20-50ms ✅ |
| Japan | Tokyo | 5-15ms ✅ |
| South Korea | Tokyo | 30-50ms ✅ |
| Hong Kong | Tokyo | 50-70ms ✅ |
| Australia | Sydney | 5-25ms ✅ |
| New Zealand | Sydney | 30-50ms ✅ |
| Brazil | São Paulo | 5-25ms ✅ |
| Argentina | São Paulo | 40-60ms ✅ |
| Chile | São Paulo | 60-80ms ✅ |
| Canada | Montreal | 5-25ms ✅ |
| Mexico | Montreal | 60-80ms ✅ |

**Legend:**
- ✅ Excellent (<100ms)
- ⚠️ Acceptable (100-150ms)

---

## 🗄️ Firestore Database Location

**Selected:** `nam5` (North America Multi-Region)

**Why nam5 instead of asia-south1?**
- ✅ **99.999% SLA** (vs 99.9% for single-region)
- ✅ **Automatic replication** across multiple US data centers
- ✅ **Better disaster recovery**
- ⚠️ **Slightly higher latency** to Asia/Europe (~50-100ms additional)

**Firestore Latency Estimates:**
- North America: 10-30ms
- Europe: 80-120ms
- Asia (via Google backbone): 100-150ms
- South America: 120-180ms
- Australia: 150-200ms

**Note:** Firestore only offers multi-region within same continent (nam5 for Americas, eur3 for Europe). There's no Asia or global multi-region option.

**Alternative:** Switch to `asia-south1` single-region for lower latency to India/Asia markets (largest IELTS user base), accepting slightly lower SLA.

---

## 💰 Cost Breakdown

### **6-Region Deployment**

**Cloud Run:**
- 6 regions × $120/month (min 1 instance each) = $720/month
- Additional scaling: ~$200/month under load
- **Total:** ~$920/month

**Firestore:**
- nam5 multi-region: ~$100/month (moderate usage)

**Gemini API:**
- Usage-based: ~$400-600/month (depends on assessment volume)

**Load Balancer + CDN:**
- Global HTTPS Load Balancer: $18/month
- CDN bandwidth: ~$40-80/month
- **Total:** ~$60/month

**Other Services:**
- Cloud Functions: ~$10/month
- Cloud DNS: $0.40/month
- Secret Manager: $5/month
- Monitoring/Logging: ~$20/month

**Monthly Total:** ~$1,515-1,715/month

### **Optimization Options**

**Option 1: Reduce to 4 Regions** (Save ~$300/month)
- Keep: Mumbai, London, Tokyo, Sydney
- Remove: São Paulo, Montreal
- Impact: Mexico uses Tokyo (~150ms), South America uses London (~180ms)
- **Cost:** ~$1,215-1,415/month

**Option 2: Reduce to 3 Regions** (Save ~$600/month)
- Keep: Mumbai, London, Tokyo
- Remove: Sydney, São Paulo, Montreal
- Impact: Australia uses Tokyo (~110ms), Americas use London
- **Cost:** ~$915-1,115/month

**Option 3: Switch Firestore to asia-south1** (Save ~$50/month)
- Better latency for India/Asia markets (largest user base)
- Accept slightly lower SLA (99.9% vs 99.999%)
- **Savings:** ~$50/month

---

## 🚀 Recommended Deployment Strategy

### **Phase 1: Launch with 3 Core Regions**
- Mumbai (India/Pakistan/Bangladesh/Middle East)
- London (UK/Europe/Africa)
- Tokyo (Japan/Korea/Hong Kong)

**Cost:** ~$915-1,115/month
**Coverage:** All major markets with <150ms latency

### **Phase 2: Expand Based on Usage**
Monitor real user metrics for 30-60 days, then add:
- Sydney (if Australia/NZ traffic is significant)
- São Paulo (if Brazil/South America traffic is significant)
- Montreal (if Canada/Mexico traffic is significant)

**Each additional region:** +$150-200/month

---

## 🔍 How Global Load Balancing Works

1. **User makes request** to www.ieltsaiprep.com
2. **Cloud DNS** resolves to Global Load Balancer IP
3. **Load Balancer** routes to **nearest healthy Cloud Run region**
4. **Cloud CDN** caches static assets at edge locations (200+ worldwide)
5. **Response** returns via Google's premium network tier

**Benefits:**
- ✅ Automatic failover if region is down
- ✅ Session affinity for WebSocket connections
- ✅ Static assets served from edge (5-20ms globally)
- ✅ Dynamic content from nearest Cloud Run region

---

## 📊 Expected Performance

**Target: <200ms p95 latency for all markets**

With 6-region deployment:
- ✅ 95% of requests: <150ms
- ✅ 99% of requests: <200ms
- ✅ South Africa edge case: 150-180ms (still acceptable)

With 3-region deployment:
- ✅ 90% of requests: <150ms
- ⚠️ Australia: 110-140ms
- ⚠️ South America: 150-200ms
- ⚠️ Canada/Mexico: 100-150ms

---

## ✅ Recommendation

**Start with 6 regions** as configured:
- Your target markets are truly global
- IELTS students expect professional, fast service
- Cost difference ($600/month) is minimal compared to poor UX
- Easier to launch with full coverage than add regions later

**After launch, monitor and optimize:**
- Use Cloud Monitoring to track actual latency by region
- Scale down underutilized regions
- Adjust Firestore location based on primary user base

---

**Current Terraform configuration supports all 6 regions. Ready to deploy!**
