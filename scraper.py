from playwright.sync_api import sync_playwright
import json
import time
import os
import requests
from urllib.parse import urlparse
import re

def download_image(url, save_dir='images'):
    """下载图片到本地"""
    if not url:
        print("Warning: Empty image URL")
        return None
        
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # 从URL中提取文件名
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = f"image_{int(time.time())}.jpg"
    
    # 确保文件名是唯一的
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(save_dir, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    
    # 下载图片
    try:
        print(f"Downloading image: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(save_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Successfully downloaded: {filepath}")
            return os.path.join(save_dir, filename)
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading image {url}: {str(e)}")
    return None

def extract_title_from_aria_label(aria_label):
    """从aria-label属性中提取视频标题"""
    if not aria_label:
        return None
    
    # 移除VIP和评分信息
    title = re.sub(r'^VIP\s+\d+\.\d+\s+', '', aria_label)
    return title.strip()

def scrape_youku_movies():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the page
        print("Navigating to Youku page...")
        page.goto('https://www.youku.com/ku/webmovie/list?filter=type_%E7%94%B5%E5%BD%B1')
        
        # Wait for initial content to load
        print("Waiting for content to load...")
        page.wait_for_selector('.yk_card_368vl')
        
        movies = []
        last_height = 0
        scroll_count = 0
        max_scrolls = 20  # 增加最大滚动次数以确保能获取足够的数据
        processed_urls = set()  # 用于跟踪已处理的URL
        
        # Scroll and collect data
        while scroll_count < max_scrolls and len(movies) < 100:  # 限制最多100条数据
            scroll_count += 1
            print(f"\nScroll attempt {scroll_count}/{max_scrolls}")
            print(f"Current movies count: {len(movies)}/100")
            
            # Scroll down
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(3)  # 等待内容加载
            
            # Get current scroll height
            current_height = page.evaluate('document.body.scrollHeight')
            
            # Break if no more content
            if current_height == last_height:
                print("No more content to load")
                break
                
            last_height = current_height
            
            # Extract movie information
            movie_cards = page.query_selector_all('.yk_card_368vl')
            print(f"Found {len(movie_cards)} movie cards on current page")
            
            for card in movie_cards:
                try:
                    link = card.query_selector('a')
                    if not link:
                        continue
                        
                    href = link.get_attribute('href')
                    if not href:
                        continue
                        
                    # Get full URL
                    video_url = f"https:{href}" if href.startswith('//') else href
                    
                    # 检查是否已处理过该URL
                    if video_url in processed_urls:
                        continue
                    
                    processed_urls.add(video_url)
                    
                    # Get title from aria-label
                    aria_label = link.get_attribute('aria-label')
                    title = extract_title_from_aria_label(aria_label)
                    
                    if not title:
                        continue
                    
                    # Get image
                    img = card.query_selector('img')
                    img_url = img.get_attribute('src') if img else None
                    
                    if not img_url:
                        print(f"Warning: No image URL found for movie: {title}")
                        continue
                    
                    # Download image if URL exists
                    local_img_path = download_image(img_url)
                    if not local_img_path:
                        print(f"Warning: Failed to download image for movie: {title}")
                        continue
                    
                    # Get score if available
                    score_element = card.query_selector('.only_score_2f-0n')
                    score = score_element.inner_text() if score_element else None
                    
                    # Get VIP tag if available
                    vip_tag = card.query_selector('.tag_YELLOW_3uzKD')
                    is_vip = bool(vip_tag)
                    
                    movie_data = {
                        'title': title,
                        'video_url': video_url,
                        'image_url': img_url,
                        'local_image_path': local_img_path,
                        'score': score,
                        'is_vip': is_vip
                    }
                    
                    movies.append(movie_data)
                    print(f"Added movie: {title}")
                    
                    # 如果已经收集到100条数据，就停止
                    if len(movies) >= 100:
                        print("\nReached target of 100 movies!")
                        break
                        
                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    continue
            
            # 如果已经收集到100条数据，就停止滚动
            if len(movies) >= 100:
                break
        
        browser.close()
        return movies

def save_to_json(movies, filename='movies.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("Starting to scrape Youku movies...")
    movies = scrape_youku_movies()
    save_to_json(movies)
    print(f"\nScraped {len(movies)} movies and saved to movies.json")
    
    # 统计图片下载情况
    total_movies = len(movies)
    movies_with_images = sum(1 for m in movies if m['local_image_path'])
    print(f"\nImage download statistics:")
    print(f"Total movies: {total_movies}")
    print(f"Movies with downloaded images: {movies_with_images}")
    print(f"Movies without images: {total_movies - movies_with_images}") 