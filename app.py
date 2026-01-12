import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import random

# ============ PAGE CONFIG ============
st.set_page_config(page_title="AgriLoop AI", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

# ============ CUSTOM CSS - LIGHT THEME ============
st.markdown("""
<style>
    /* Force light theme */
    .stApp { background-color: #f9fafb !important; }
    
    .main-header { background: linear-gradient(135deg, #16a34a 0%, #15803d 100%); padding: 1.5rem 2rem; border-radius: 1rem; color: white; margin-bottom: 2rem; }
    .main-header h1 { color: white !important; margin: 0; font-size: 2.5rem; }
    .main-header p { color: #bbf7d0; margin: 0.5rem 0 0 0; font-size: 1.1rem; }
    
    .metric-card { background: white !important; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; border: 1px solid #e5e7eb; }
    .metric-card .value { font-size: 2rem; font-weight: bold; margin-bottom: 0.25rem; }
    .metric-card .label { color: #6b7280 !important; font-size: 0.875rem; }
    
    .green { color: #16a34a !important; } 
    .blue { color: #2563eb !important; } 
    .orange { color: #ea580c !important; } 
    .purple { color: #9333ea !important; } 
    .red { color: #dc2626 !important; }
    
    .feature-card { background: white !important; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; margin-bottom: 1rem; }
    .feature-card .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .feature-card h3 { font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem; color: #111827 !important; }
    .feature-card p { color: #6b7280 !important; font-size: 0.875rem; }
    
    .card { background: white !important; color: #111827 !important; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; border: 1px solid #e5e7eb; }
    .card h4 { color: #111827 !important; margin: 0 0 0.5rem 0; }
    .card p { color: #4b5563 !important; margin: 0.25rem 0; }
    
    .partner-card { background: white !important; color: #111827 !important; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; margin-bottom: 1rem; }
    .partner-card h4 { color: #111827 !important; font-size: 1.1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
    .partner-card .type { color: #16a34a !important; font-size: 0.9rem; text-transform: capitalize; margin: 0.25rem 0; }
    .partner-card .capacity { color: #6b7280 !important; font-size: 0.875rem; margin: 0.25rem 0; }
    .partner-card .rating { color: #eab308 !important; font-size: 0.9rem; margin-top: 0.5rem; }
    
    .result-box { background: #f0fdf4 !important; border: 1px solid #bbf7d0; padding: 1.5rem; border-radius: 0.75rem; margin: 1rem 0; }
    .result-box h3 { color: #15803d !important; }
    
    .stats-section { background: #f0fdf4 !important; padding: 2rem; border-radius: 0.75rem; margin: 2rem 0; }
    
    .footer { background: #1f2937 !important; color: white !important; padding: 1.5rem; text-align: center; margin-top: 2rem; border-radius: 0.75rem; }
    .footer p { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ============ INIT SESSION STATE ============
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin': {'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'email': 'admin@agriloop.com', 
                  'full_name': 'System Admin', 'role': 'admin', 'phone': '', 'created_at': datetime.now().isoformat()}
    }
if 'farms' not in st.session_state:
    st.session_state.farms = []
if 'crops' not in st.session_state:
    st.session_state.crops = []
if 'advisories' not in st.session_state:
    st.session_state.advisories = []
if 'surplus_listings' not in st.session_state:
    st.session_state.surplus_listings = []
if 'waste_requests' not in st.session_state:
    st.session_state.waste_requests = []
if 'partners' not in st.session_state:
    st.session_state.partners = [
        {'id': 1, 'name': 'GreenCompost Co', 'type': 'compost_facility', 'capacity': 5000, 'lat': 28.6139, 'lng': 77.2090, 'rating': 4.5},
        {'id': 2, 'name': 'BioGas Solutions', 'type': 'biogas_plant', 'capacity': 10000, 'lat': 28.7041, 'lng': 77.1025, 'rating': 4.2},
        {'id': 3, 'name': 'FoodBank Network', 'type': 'food_bank', 'capacity': 2000, 'lat': 28.5355, 'lng': 77.3910, 'rating': 4.8},
    ]

# ============ HELPER FUNCTIONS ============
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def get_user_farms(): return [f for f in st.session_state.farms if f['owner'] == st.session_state.current_user] if st.session_state.current_user else []
def get_user_crops(): return [c for c in st.session_state.crops if c['owner'] == st.session_state.current_user] if st.session_state.current_user else []
def get_active_crops(): return [c for c in get_user_crops() if c['status'] == 'active']
def get_farm_crops(fid): return [c for c in st.session_state.crops if c['farm_id'] == fid]

def get_irrigation_rec(soil_moisture, temp, humidity, rainfall, crop_name, area):
    water_stress = max(0, (100 - soil_moisture) / 100)
    evap = (temp * 0.1) + ((100 - humidity) * 0.05)
    rain_factor = max(0, 1 - (rainfall / 50))
    volume = area * 1000 * water_stress * evap * rain_factor
    
    if soil_moisture < 30: freq, urg = 1, "high"
    elif soil_moisture < 50: freq, urg = 2, "medium"
    elif soil_moisture < 70: freq, urg = 3, "low"
    else: freq, urg = 5, "none"
    
    risks = []
    if temp > 35: risks.append("High temperature stress")
    if soil_moisture < 25: risks.append("Critical moisture deficit")
    if humidity < 30: risks.append("Low humidity")
    
    if urg == "high": rec = f"🚨 Immediate irrigation needed for {crop_name}. Soil moisture critically low at {soil_moisture}%."
    elif urg == "medium": rec = f"⚠️ Schedule irrigation within 24-48 hours for {crop_name}. Moisture: {soil_moisture}%."
    elif urg == "low": rec = f"📊 Monitor {crop_name}. Irrigation may be needed in 2-3 days. Moisture: {soil_moisture}%."
    else: rec = f"✅ No immediate irrigation needed for {crop_name}. Moisture adequate at {soil_moisture}%."
    
    return {"recommendation": rec, "volume": max(0, volume), "frequency": freq, "urgency": urg, "risks": risks}

def predict_yield(crop, area, soil):
    yields = {"wheat": 3500, "rice": 4000, "corn": 8000, "maize": 8000, "potato": 25000, "tomato": 50000}
    base = yields.get(crop.lower(), 5000)
    mult = {"loamy": 1.2, "clay": 0.9, "sandy": 0.8, "silty": 1.1}.get(soil, 1.0) if soil else 1.0
    return round(base * area * mult * random.uniform(0.9, 1.1), 2)

def predict_surplus(yield_kg, demand, storage):
    surplus = max(0, yield_kg - demand)
    pct = (surplus / yield_kg * 100) if yield_kg > 0 else 0
    if pct > 30: cat, urg = "high", "high"
    elif pct > 15: cat, urg = "medium", "medium"
    elif pct > 5: cat, urg = "low", "low"
    else: cat, urg = "minimal", "none"
    recs = []
    if surplus > storage: recs.append("⚠️ Surplus exceeds storage - sell immediately")
    if cat == "high": recs.extend(["🏦 Connect with food banks", "🏭 Consider processing"])
    if cat in ["high", "medium"]: recs.append("📦 List on marketplace")
    return {"surplus": round(surplus, 2), "pct": round(pct, 2), "category": cat, "urgency": urg, "recs": recs}

# ============ NAVIGATION FUNCTIONS ============
def go_to(page):
    st.session_state.page = page

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = 'home'

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🌾 AgriLoop AI")
    st.caption("Smart Farming Platform")
    st.divider()
    
    if st.session_state.logged_in:
        user = st.session_state.users[st.session_state.current_user]
        st.success(f"👤 {user['full_name'] or st.session_state.current_user}")
        st.caption(f"Role: {user['role'].title()}")
        st.divider()
        
        if st.button("🏠 Dashboard", use_container_width=True): go_to('dashboard')
        if st.button("🌱 My Farms", use_container_width=True): go_to('farms')
        if st.button("💧 Advisory", use_container_width=True): go_to('advisory')
        if st.button("📦 Surplus", use_container_width=True): go_to('surplus')
        if st.button("♻️ Circular Economy", use_container_width=True): go_to('circular')
        
        # Admin Panel - always show for admin users
        if user['role'] == 'admin':
            st.divider()
            st.markdown("**Admin**")
            if st.button("🔧 Admin Panel", use_container_width=True, type="primary"): 
                go_to('admin')
                st.rerun()
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    else:
        if st.button("🏠 Home", use_container_width=True): go_to('home')
        if st.button("🔐 Login", use_container_width=True): go_to('login')
        if st.button("📝 Register", use_container_width=True): go_to('register')
    
    st.divider()
    st.caption("© 2024 AgriLoop AI")

# ============ PAGES ============
page = st.session_state.page

# ---------- HOME PAGE ----------
if not st.session_state.logged_in and page == 'home':
    st.markdown("""<div class="main-header"><h1>🌾 AgriLoop AI</h1><p>AI-Powered Agricultural Platform for Smart Farming & Circular Economy</p></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🚀 Get Started", use_container_width=True, type="primary"):
            go_to('register')
            st.rerun()
    with col2:
        if st.button("🔐 Login", use_container_width=True):
            go_to('login')
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Platform Features")
    
    features = [
        ("💧", "Smart Irrigation", "AI-powered irrigation recommendations based on soil moisture, weather, and crop conditions."),
        ("📊", "Crop Advisory", "Get personalized crop advisory and yield predictions to maximize your harvest."),
        ("🔄", "Circular Economy", "Convert food waste into value through compost, biogas, and upcycling networks."),
        ("📈", "Surplus Prediction", "Predict crop surplus before harvest and connect with buyers and waste converters."),
        ("🚚", "Logistics", "Optimized routing and pickup scheduling for waste and surplus collection."),
        ("🌱", "Sustainability", "Track your environmental impact: water saved, waste diverted, emissions reduced."),
    ]
    
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""<div class="feature-card"><div class="icon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>""", unsafe_allow_html=True)
    
    st.markdown("""<div class="stats-section"><h2 style="text-align:center;margin-bottom:1.5rem;">Platform Capabilities</h2></div>""", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (t, s) in zip(cols, [("🤖 AI-Powered", "ML Models"), ("⚡ Real-time", "Weather Data"), ("📈 Scalable", "Production Ready"), ("🔌 Open API", "RESTful")]):
        with col:
            st.markdown(f"""<div style="text-align:center;"><div style="font-size:1.25rem;font-weight:bold;color:#16a34a;">{t}</div><div style="color:#6b7280;">{s}</div></div>""", unsafe_allow_html=True)

# ---------- LOGIN PAGE ----------
elif not st.session_state.logged_in and page == 'login':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="card" style="text-align:center;padding:2rem;"><h1>🌾 AgriLoop AI</h1><h2>Login</h2></div>""", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username in st.session_state.users:
                if st.session_state.users[username]['password'] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
            else:
                st.error("❌ User not found")
        
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Register here", use_container_width=True):
            go_to('register')
            st.rerun()

# ---------- REGISTER PAGE ----------
elif not st.session_state.logged_in and page == 'register':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="card" style="text-align:center;padding:2rem;"><h1>🌾 AgriLoop AI</h1><h2>Register</h2></div>""", unsafe_allow_html=True)
        
        email = st.text_input("Email *", placeholder="your@email.com")
        username = st.text_input("Username *", placeholder="Choose a username")
        full_name = st.text_input("Full Name", placeholder="Your full name")
        phone = st.text_input("Phone (Optional)")
        role = st.selectbox("Role *", ["farmer", "processor", "waste_converter"])
        password = st.text_input("Password *", type="password", placeholder="Choose a password")
        
        if st.button("Register", use_container_width=True, type="primary"):
            if not email or not username or not password:
                st.error("❌ Please fill all required fields")
            elif username in st.session_state.users:
                st.error("❌ Username already exists")
            else:
                st.session_state.users[username] = {
                    'password': hash_pw(password), 'email': email, 'full_name': full_name,
                    'role': role, 'phone': phone, 'created_at': datetime.now().isoformat()
                }
                st.success("✅ Registration successful! Please login.")
                st.session_state.page = 'login'
                st.rerun()
        
        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Login here", use_container_width=True):
            go_to('login')
            st.rerun()

# ---------- DASHBOARD PAGE ----------
elif st.session_state.logged_in and page == 'dashboard':
    user = st.session_state.users[st.session_state.current_user]
    st.title("🏠 Farmer Dashboard")
    st.caption(f"Welcome back, {user['full_name'] or st.session_state.current_user}!")
    
    uf = get_user_farms()
    uc = get_active_crops()
    ua = [a for a in st.session_state.advisories if a['user'] == st.session_state.current_user]
    us = [s for s in st.session_state.surplus_listings if s['user'] == st.session_state.current_user]
    
    cols = st.columns(4)
    for col, (val, label, color) in zip(cols, [(len(uf), "Farms", "green"), (len(uc), "Active Crops", "blue"), (len(us), "Surplus Listings", "orange"), (len(ua), "Advisories", "purple")]):
        with col:
            st.markdown(f"""<div class="metric-card"><div class="value {color}">{val}</div><div class="label">{label}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Quick Actions")
    cols = st.columns(3)
    with cols[0]:
        if st.button("🌱 Manage Farms", use_container_width=True, type="primary"):
            go_to('farms')
            st.rerun()
    with cols[1]:
        if st.button("💧 Get Advisory", use_container_width=True):
            go_to('advisory')
            st.rerun()
    with cols[2]:
        if st.button("📦 Manage Surplus", use_container_width=True):
            go_to('surplus')
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recent Advisories")
        if ua:
            for a in ua[-3:][::-1]:
                st.info(f"**{a['type'].title()}** - {a.get('recommendation', '')[:80]}...")
        else:
            st.caption("No advisories yet. Request one to get started.")
    with col2:
        st.subheader("Recent Surplus")
        if us:
            for s in us[-3:][::-1]:
                st.success(f"**{s['quantity']} kg** - {s.get('crop', 'N/A')} ({s['harvest_date']})")
        else:
            st.caption("No surplus listings yet.")

# ---------- FARMS PAGE ----------
elif st.session_state.logged_in and page == 'farms':
    st.title("🌱 My Farms")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        show_form = st.button("➕ Add Farm", use_container_width=True, type="primary")
    
    if show_form or st.session_state.get('show_farm_form'):
        st.session_state.show_farm_form = True
        with st.expander("Add New Farm", expanded=True):
            with st.form("add_farm"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Farm Name *")
                area = c2.number_input("Area (Hectares) *", min_value=0.01, value=1.0)
                c1, c2 = st.columns(2)
                lat = c1.number_input("Latitude *", value=28.6139, format="%.6f")
                lng = c2.number_input("Longitude *", value=77.2090, format="%.6f")
                address = st.text_input("Address")
                soil = st.selectbox("Soil Type", ["", "clay", "sandy", "loamy", "silty", "peaty", "chalky"])
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("Add Farm", use_container_width=True, type="primary"):
                    if name:
                        st.session_state.farms.append({
                            'id': len(st.session_state.farms) + 1, 'name': name, 'area_hectares': area,
                            'location_latitude': lat, 'location_longitude': lng, 'location_address': address,
                            'soil_type': soil or None, 'owner': st.session_state.current_user, 'created_at': datetime.now().isoformat()
                        })
                        st.session_state.show_farm_form = False
                        st.success(f"✅ Farm '{name}' added!")
                        st.rerun()
                if c2.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_farm_form = False
                    st.rerun()
    
    farms = get_user_farms()
    if not farms:
        st.info("No farms yet. Click 'Add Farm' to get started.")
    else:
        for farm in farms:
            with st.container():
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.markdown(f"### 🏡 {farm['name']}")
                    location_display = farm.get('location_address') or f"({farm['location_latitude']}, {farm['location_longitude']})"
                    st.caption(f"{farm['area_hectares']} hectares | {farm.get('soil_type') or 'Unknown soil'} | {location_display}")
                with c3:
                    if st.button("🗑️", key=f"del_{farm['id']}"):
                        st.session_state.farms = [f for f in st.session_state.farms if f['id'] != farm['id']]
                        st.session_state.crops = [c for c in st.session_state.crops if c['farm_id'] != farm['id']]
                        st.rerun()
                
                crops = get_farm_crops(farm['id'])
                with st.expander(f"🌾 Crops ({len(crops)})"):
                    if crops:
                        for c in crops:
                            st.write(f"• **{c['crop_name']}** - {c['area_hectares']} ha ({c['status']})")
                    else:
                        st.caption("No crops yet")
                    
                    st.markdown("---")
                    st.markdown("**Add Crop**")
                    with st.form(f"crop_{farm['id']}"):
                        c1, c2 = st.columns(2)
                        cn = c1.text_input("Crop Name", key=f"cn{farm['id']}")
                        ca = c2.number_input("Area (ha)", min_value=0.01, value=0.5, key=f"ca{farm['id']}")
                        c1, c2 = st.columns(2)
                        pd = c1.date_input("Planting Date", key=f"pd{farm['id']}")
                        hd = c2.date_input("Harvest Date", key=f"hd{farm['id']}")
                        if st.form_submit_button("Add Crop"):
                            if cn:
                                st.session_state.crops.append({
                                    'id': len(st.session_state.crops) + 1, 'farm_id': farm['id'], 'crop_name': cn,
                                    'area_hectares': ca, 'planting_date': pd.isoformat(), 'expected_harvest_date': hd.isoformat(),
                                    'status': 'active', 'owner': st.session_state.current_user
                                })
                                st.success(f"✅ Crop '{cn}' added!")
                                st.rerun()
                st.divider()

# ---------- ADVISORY PAGE ----------
elif st.session_state.logged_in and page == 'advisory':
    st.title("💧 Crop Advisory")
    
    crops = get_active_crops()
    
    st.subheader("🤖 AI Irrigation Recommendation")
    if not crops:
        st.warning("⚠️ Add farms and crops first to get irrigation advice.")
    else:
        with st.form("irrigation"):
            c1, c2 = st.columns(2)
            with c1:
                opts = {}
                for c in crops:
                    f = next((f for f in st.session_state.farms if f['id'] == c['farm_id']), None)
                    opts[f"{f['name'] if f else 'Farm'} - {c['crop_name']}"] = c
                sel = st.selectbox("Select Crop *", list(opts.keys()))
                crop = opts[sel]
                soil_m = st.slider("Soil Moisture (%)", 0, 100, 50)
                temp = st.slider("Temperature (°C)", 0, 50, 25)
            with c2:
                humid = st.slider("Humidity (%)", 0, 100, 60)
                rain = st.slider("Rainfall (mm, last 7 days)", 0, 100, 0)
            
            if st.form_submit_button("🔮 Get Recommendation", use_container_width=True, type="primary"):
                r = get_irrigation_rec(soil_m, temp, humid, rain, crop['crop_name'], crop['area_hectares'])
                
                st.markdown("""<div class="result-box"><h3>📊 Recommendation</h3></div>""", unsafe_allow_html=True)
                cols = st.columns(4)
                cols[0].metric("💧 Volume", f"{r['volume']:.1f} L")
                cols[1].metric("📅 Frequency", f"Every {r['frequency']} days")
                urg_icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "none": "⚪"}.get(r['urgency'], "")
                cols[2].metric("⚡ Urgency", f"{urg_icon} {r['urgency'].title()}")
                cols[3].metric("Status", "Action Needed" if r['volume'] > 100 else "OK")
                
                st.info(r['recommendation'])
                if r['risks']:
                    st.warning("**Risk Factors:** " + ", ".join(r['risks']))
                
                st.session_state.advisories.append({
                    'id': len(st.session_state.advisories) + 1, 'user': st.session_state.current_user,
                    'crop_id': crop['id'], 'type': 'irrigation', 'status': 'completed',
                    'recommendation': r['recommendation'], 'volume': r['volume'], 'frequency': r['frequency'],
                    'created_at': datetime.now().isoformat()
                })
    
    st.divider()
    st.subheader("📋 Advisory History")
    ua = [a for a in st.session_state.advisories if a['user'] == st.session_state.current_user]
    if ua:
        for a in ua[-10:][::-1]:
            st.markdown(f"""<div class="card"><strong>{a['type'].title()}</strong> <span style="color:#6b7280;">- {a.get('created_at', '')[:10]}</span><p>{a.get('recommendation', '')}</p></div>""", unsafe_allow_html=True)
    else:
        st.info("No advisories yet.")

# ---------- SURPLUS PAGE ----------
elif st.session_state.logged_in and page == 'surplus':
    st.title("📦 Surplus Management")
    
    crops = get_active_crops()
    
    c1, c2 = st.columns([4, 1])
    with c2:
        show_surplus = st.button("➕ Add Listing", use_container_width=True, type="primary")
    
    st.subheader("🔮 Predict Surplus")
    if not crops:
        st.warning("⚠️ Add crops first to predict surplus.")
    else:
        with st.form("predict"):
            c1, c2 = st.columns(2)
            with c1:
                opts = {}
                for c in crops:
                    f = next((f for f in st.session_state.farms if f['id'] == c['farm_id']), None)
                    opts[f"{f['name'] if f else 'Farm'} - {c['crop_name']}"] = (c, f)
                sel = st.selectbox("Select Crop *", list(opts.keys()))
                crop, farm = opts[sel]
                demand = st.number_input("Market Demand (kg)", min_value=0, value=1000)
            with c2:
                storage = st.number_input("Storage Capacity (kg)", min_value=0, value=500)
            
            if st.form_submit_button("📊 Predict", use_container_width=True, type="primary"):
                yld = predict_yield(crop['crop_name'], crop['area_hectares'], farm.get('soil_type') if farm else None)
                r = predict_surplus(yld, demand, storage)
                
                st.markdown("""<div class="result-box"><h3>📊 Prediction Results</h3></div>""", unsafe_allow_html=True)
                cols = st.columns(4)
                cols[0].metric("🌾 Yield", f"{yld:,.0f} kg")
                cols[1].metric("📦 Surplus", f"{r['surplus']:,.0f} kg")
                cols[2].metric("📊 Percentage", f"{r['pct']:.1f}%")
                urg_icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "none": "⚪"}.get(r['urgency'], "")
                cols[3].metric("⚡ Urgency", f"{urg_icon} {r['urgency'].title()}")
                
                if r['recs']:
                    st.subheader("💡 Recommendations")
                    for rec in r['recs']:
                        st.write(f"• {rec}")
    
    st.divider()
    
    if show_surplus or st.session_state.get('show_surplus_form'):
        st.session_state.show_surplus_form = True
        if crops:
            with st.expander("Add Surplus Listing", expanded=True):
                with st.form("add_surplus"):
                    crop_opts = {c['crop_name']: c for c in crops}
                    sel_crop = st.selectbox("Crop *", list(crop_opts.keys()))
                    c1, c2 = st.columns(2)
                    qty = c1.number_input("Quantity (kg) *", min_value=1, value=100)
                    hdate = c2.date_input("Harvest Date *")
                    price = st.number_input("Price per kg (optional)", min_value=0.0, value=0.0)
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("Add Listing", use_container_width=True, type="primary"):
                        st.session_state.surplus_listings.append({
                            'id': len(st.session_state.surplus_listings) + 1, 'user': st.session_state.current_user,
                            'crop_id': crop_opts[sel_crop]['id'], 'crop': sel_crop, 'quantity': qty,
                            'harvest_date': hdate.isoformat(), 'unit_price': price if price > 0 else None,
                            'status': 'available', 'created_at': datetime.now().isoformat()
                        })
                        st.session_state.show_surplus_form = False
                        st.success("✅ Listing added!")
                        st.rerun()
                    if c2.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_surplus_form = False
                        st.rerun()
    
    st.subheader("📋 Surplus Listings")
    us = [s for s in st.session_state.surplus_listings if s['user'] == st.session_state.current_user]
    if us:
        for s in us[::-1]:
            st.markdown(f"""<div class="card"><h4>{s['quantity']} kg - {s.get('crop', 'N/A')}</h4><p>📅 {s['harvest_date']} | {'💰 $' + str(s['unit_price']) + '/kg' if s.get('unit_price') else 'No price set'}</p><span style="background:#fed7aa;color:#c2410c;padding:0.25rem 0.5rem;border-radius:0.25rem;font-size:0.75rem;">{s['status'].title()}</span></div>""", unsafe_allow_html=True)
    else:
        st.info("No surplus listings yet.")

# ---------- CIRCULAR ECONOMY PAGE ----------
elif st.session_state.logged_in and page == 'circular':
    st.title("♻️ Circular Economy Marketplace")
    
    c1, c2 = st.columns([4, 1])
    with c2:
        show_waste = st.button("➕ Create Request", use_container_width=True, type="primary")
    
    st.subheader("🤝 Available Partners")
    cols = st.columns(3)
    for i, p in enumerate(st.session_state.partners):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="partner-card">
                <h4>{p['name']}</h4>
                <p class="type">{p['type'].replace('_', ' ')}</p>
                <p class="capacity">Capacity: {p['capacity']} kg/day</p>
                <p class="rating">{'⭐' * int(p['rating'])} ({p['rating']})</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    if show_waste or st.session_state.get('show_waste_form'):
        st.session_state.show_waste_form = True
        with st.expander("Create Waste Request", expanded=True):
            with st.form("waste_req"):
                wtype = st.selectbox("Waste Type *", ["crop_residue", "food_waste", "organic_waste", "surplus_produce", "spoiled_produce"])
                c1, c2 = st.columns(2)
                qty = c1.number_input("Quantity (kg) *", min_value=1, value=100)
                lat = c2.number_input("Latitude *", value=28.6139, format="%.6f")
                c1, c2 = st.columns(2)
                lng = c1.number_input("Longitude *", value=77.2090, format="%.6f")
                addr = c2.text_input("Address (optional)")
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("Create Request", use_container_width=True, type="primary"):
                    st.session_state.waste_requests.append({
                        'id': len(st.session_state.waste_requests) + 1, 'user': st.session_state.current_user,
                        'waste_type': wtype, 'quantity_kg': qty, 'location_latitude': lat,
                        'location_longitude': lng, 'location_address': addr, 'status': 'pending',
                        'partner_id': None, 'created_at': datetime.now().isoformat()
                    })
                    st.session_state.show_waste_form = False
                    st.success("✅ Request created!")
                    st.rerun()
                if c2.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_waste_form = False
                    st.rerun()
    
    st.subheader("📋 My Waste Requests")
    ur = [r for r in st.session_state.waste_requests if r['user'] == st.session_state.current_user]
    if ur:
        for r in ur[::-1]:
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"""
                <div class="card">
                    <h4 style="text-transform:capitalize;">{r['waste_type'].replace('_', ' ')}</h4>
                    <p>{r['quantity_kg']} kg | {r.get('created_at', '')[:10]}</p>
                    {'<p style="color:#16a34a !important;">✅ Matched with partner</p>' if r.get('partner_id') else ''}
                </div>
                """, unsafe_allow_html=True)
            with c2:
                colors = {'pending': '🟡', 'matched': '🟢', 'completed': '✅'}
                st.write(f"{colors.get(r['status'], '⚪')} {r['status'].title()}")
            with c3:
                if r['status'] == 'pending':
                    if st.button("🔗 Match", key=f"m{r['id']}"):
                        if st.session_state.partners:
                            r['partner_id'] = st.session_state.partners[0]['id']
                            r['status'] = 'matched'
                            st.success(f"✅ Matched with {st.session_state.partners[0]['name']}!")
                            st.rerun()
    else:
        st.info("No waste requests yet.")

# ---------- ADMIN PAGE ----------
elif st.session_state.logged_in and page == 'admin':
    user = st.session_state.users[st.session_state.current_user]
    if user['role'] != 'admin':
        st.error("❌ Admin access required")
        st.stop()
    
    st.title("🔧 Admin Panel")
    
    cols = st.columns(4)
    for col, (val, label, color) in zip(cols, [(len(st.session_state.users), "Users", "blue"), (len(st.session_state.farms), "Farms", "green"), (len(st.session_state.crops), "Crops", "orange"), (len(st.session_state.advisories), "Advisories", "purple")]):
        with col:
            st.markdown(f"""<div class="metric-card"><div class="value {color}">{val}</div><div class="label">{label}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Role distribution
    st.subheader("👥 User Distribution")
    roles = {'farmer': 0, 'processor': 0, 'waste_converter': 0, 'admin': 0}
    for u in st.session_state.users.values():
        r = u.get('role', 'farmer')
        if r in roles: roles[r] += 1
    
    cols = st.columns(4)
    for col, (role, count) in zip(cols, roles.items()):
        with col:
            st.metric(role.replace('_', ' ').title(), count)
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["👥 Users", "🌱 Farms", "🤝 Partners"])
    
    with tab1:
        st.subheader("User Management")
        data = [{'Username': u, 'Email': d['email'], 'Name': d.get('full_name', ''), 'Role': d['role']} for u, d in st.session_state.users.items()]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("Change Role")
        others = [u for u in st.session_state.users.keys() if u != st.session_state.current_user]
        if others:
            c1, c2, c3 = st.columns(3)
            sel_u = c1.selectbox("User", others)
            new_r = c2.selectbox("New Role", ["farmer", "processor", "waste_converter", "admin"])
            with c3:
                st.write("")
                st.write("")
                if st.button("Update"):
                    st.session_state.users[sel_u]['role'] = new_r
                    st.success(f"✅ Updated {sel_u} to {new_r}")
                    st.rerun()
        
        st.subheader("Delete User")
        if others:
            c1, c2 = st.columns([2, 1])
            del_u = c1.selectbox("Select User", others, key="del")
            with c2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete"):
                    del st.session_state.users[del_u]
                    st.session_state.farms = [f for f in st.session_state.farms if f['owner'] != del_u]
                    st.session_state.crops = [c for c in st.session_state.crops if c['owner'] != del_u]
                    st.success(f"✅ Deleted {del_u}")
                    st.rerun()
    
    with tab2:
        st.subheader("All Farms")
        if st.session_state.farms:
            data = [{'ID': f['id'], 'Name': f['name'], 'Area': f['area_hectares'], 'Owner': f['owner']} for f in st.session_state.farms]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("No farms yet")
    
    with tab3:
        st.subheader("Partners")
        if st.session_state.partners:
            data = [{'ID': p['id'], 'Name': p['name'], 'Type': p['type'], 'Capacity': p['capacity'], 'Rating': p['rating']} for p in st.session_state.partners]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("Add Partner")
        with st.form("add_partner"):
            c1, c2 = st.columns(2)
            pname = c1.text_input("Name *")
            ptype = c2.selectbox("Type", ["compost_facility", "biogas_plant", "food_bank", "recycling_center"])
            c1, c2, c3 = st.columns(3)
            cap = c1.number_input("Capacity (kg/day)", min_value=1, value=1000)
            plat = c2.number_input("Latitude", value=28.6139, format="%.6f")
            plng = c3.number_input("Longitude", value=77.2090, format="%.6f")
            
            if st.form_submit_button("Add Partner", use_container_width=True, type="primary"):
                if pname:
                    st.session_state.partners.append({
                        'id': len(st.session_state.partners) + 1, 'name': pname, 'type': ptype,
                        'capacity': cap, 'lat': plat, 'lng': plng, 'rating': 0
                    })
                    st.success(f"✅ Partner '{pname}' added!")
                    st.rerun()

# ---------- FOOTER ----------
st.markdown("""<div class="footer"><p>© 2024 AgriLoop AI. All rights reserved.</p></div>""", unsafe_allow_html=True)
