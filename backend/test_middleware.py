# test_middleware.py
import requests

def test_permission(email, password, endpoint, method='GET'):
    """Test if a user can access an endpoint"""
    # Login
    session = requests.Session()
    
    # Step 1
    resp = session.post('http://localhost:5000/api/auth/login/step1', 
                        json={'email': email, 'password': password})
    if resp.json().get('requires_otp'):
        otp = input(f"Enter OTP for {email}: ")
        session.post('http://localhost:5000/api/auth/login/step2',
                     json={'email': email, 'otp_code': otp})
    
    # Test endpoint
    if method == 'GET':
        resp = session.get(f'http://localhost:5000{endpoint}')
    else:
        resp = session.post(f'http://localhost:5000{endpoint}')
    
    print(f"{email} -> {method} {endpoint}: {resp.status_code}")
    return resp.status_code

if __name__ == '__main__':
    # Test admin user
    test_permission('daltonoyigo489@gmail.com', 'Admin123!', '/api/admin/users')
    test_permission('daltonoyigo489@gmail.com', 'Admin123!', '/api/admin/users/1', 'DELETE')
    
    # Test partner user
    test_permission('daltonmartin472@gmail.com', 'Admin123!', '/api/admin/users')