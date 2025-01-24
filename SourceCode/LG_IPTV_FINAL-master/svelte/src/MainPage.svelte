<script>
  import { onMount } from 'svelte';
  let recommendations = []; // Recommendations 전달 받음
  let categories = [];  // Recommendations 기반으로 생성
  export let userId = null;
  let videos = {};
  let pageTokens = {};
  let selectedCategory = null;
  let selectedVideo = null;
  let showModal = false;
  let selectedIndex = 0;
  let focusArea = 'category';
  let scrollContainer;
  let isLoadingMore = false;

  // Recommendations에서 categories 추출
  // 카테고리 기반 영상 로드
  onMount(async () => {
    console.log('onMount called with userId:', userId);
    if (userId === null) {
      console.error('User ID is null');
      return;
    }
    try {
      console.log('Fetching recommendations for userId:', userId);
      // 추천 데이터 요청
      const recommendResponse = await fetch(`/api/recommendations/${userId}`);
      if (!recommendResponse.ok) {
        console.error('Failed to fetch recommendations:', recommendResponse.statusText);
        return;
      }

      const recommendResult = await recommendResponse.json();
      console.log('Recommendations fetched:', recommendResult);
      recommendations = Array.isArray(recommendResult.recommendations) ? recommendResult.recommendations : [];
      categories = Array.isArray(recommendResult.categories) ? recommendResult.categories : [];
      console.log('Categories:', categories); // 디버그용 로그 추가

      // 카테고리 추출 및 초기화
      if (categories.length > 0) {
        selectedCategory = categories[0];
        await loadVideosForCategory(selectedCategory);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  });

  async function fetchVideos(category, pageToken = '') {
    try {
      const response = await fetch(`/api/videos/search/${category}${pageToken ? `?pageToken=${pageToken}` : ''}&regionCode=KR`);
      const data = await response.json();
      pageTokens[category] = data.nextPageToken || null;
      return data.videos.map(video => ({
        id: { videoId: video.id.videoId },
        snippet: {
          title: video.snippet.title,
          thumbnails: { high: { url: video.snippet.thumbnails.high.url } },
          duration: video.contentDetails ? video.contentDetails.duration : 0,
        },
      }));
    } catch (error) {
      console.error(`Error fetching videos for category "${category}":`, error);
      return [];
    }
  }

  async function loadVideosForCategory(category) {
    if (!videos[category]) {
      videos[category] = await fetchVideos(category);
    }
  }

  async function loadMoreVideos() {
    if (isLoadingMore || !pageTokens[selectedCategory]) return;

    isLoadingMore = true;
    const newVideos = await fetchVideos(selectedCategory, pageTokens[selectedCategory]);
    if (newVideos.length > 0) {
      videos[selectedCategory] = [...videos[selectedCategory], ...newVideos];
      videos = { ...videos };
    }
    isLoadingMore = false;
  }

  function selectCategory(category) {
    selectedCategory = category;
    if (!videos[category]) {
      loadVideosForCategory(category);
    }
  }

  function openVideo(video) {
    selectedVideo = video;
    //saveVideo(video, userId);
    showModal = true;
  }

  async function saveVideo(video, userId) {
    try {
      const response = await fetch(`/api/videos/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          user_id: userId, // 전달받은 userId 활용
          video_id: video.id.videoId,
          title: video.snippet.title,
          video_length: video.duration, // 영상 길이
          category: selectedCategory,
        }),
      });

      if (!response.ok) {
        console.error('Failed to save video:', await response.text());
        return;
      }
      console.log('Video saved successfully');
    } catch (error) {
      console.error('Error saving video:', error);
    }
  }

  function parseDuration(duration) {
    if (!duration) return '';
    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = duration % 60;
    return `${hours > 0 ? hours + '시간 ' : ''}${minutes}분 ${seconds}초`;
  }

  function closeModal() {
    showModal = false;
    selectedVideo = null;
  }

  function scrollToSelectedCard() {
    if (focusArea === 'video' && scrollContainer) {
      const selectedCard = scrollContainer.querySelector(`.video-card:nth-child(${selectedIndex + 1}), .load-more-button`);
      if (selectedCard) {
        const containerWidth = scrollContainer.offsetWidth;
        const cardLeft = selectedCard.offsetLeft;
        const cardWidth = selectedCard.offsetWidth;

        const scrollPosition = cardLeft - (containerWidth / 2) + (cardWidth / 2);
        scrollContainer.scrollTo({
          left: scrollPosition,
          behavior: 'smooth'
        });
      }
    }
  }

  function handleKeydown(event) {
    if (showModal) {
      if (event.key === 'Escape') closeModal();
      return;
    }

    const currentVideos = Array.isArray(videos[selectedCategory]) ? videos[selectedCategory] : [];
    const categoryIndex = categories.indexOf(selectedCategory);
    const maxIndex = currentVideos.length + (pageTokens[selectedCategory] ? 1 : 0);

    switch(event.key) {
      case 'ArrowUp':
        event.preventDefault();
        if (focusArea === 'video') {
          focusArea = 'category';
        }
        break;
      case 'ArrowDown':
        event.preventDefault();
        if (focusArea === 'category') {
          focusArea = 'video';
          selectedIndex = 0;
          scrollToSelectedCard();
        }
        break;
      case 'ArrowRight':
        event.preventDefault();
        if (focusArea === 'category') {
          const nextCategoryIndex = (categoryIndex + 1) % categories.length;
          selectedCategory = categories[nextCategoryIndex];
          selectedIndex = 0;
          if (!videos[selectedCategory]) {
            fetchVideos(selectedCategory).then(result => {
              videos[selectedCategory] = result;
              videos = {...videos};
            });
          }
        } else {
          selectedIndex = (selectedIndex + 1) % maxIndex;
          scrollToSelectedCard();
        }
        break;
      case 'ArrowLeft':
        event.preventDefault();
        if (focusArea === 'category') {
          const prevCategoryIndex = categoryIndex === 0 ? categories.length - 1 : categoryIndex - 1;
          selectedCategory = categories[prevCategoryIndex];
          selectedIndex = 0;
          if (!videos[selectedCategory]) {
            fetchVideos(selectedCategory).then(result => {
              videos[selectedCategory] = result;
              videos = {...videos};
            });
          }
        } else {
          selectedIndex = selectedIndex === 0 ? maxIndex - 1 : selectedIndex - 1;
          scrollToSelectedCard();
        }
        break;
      case 'Enter':
        event.preventDefault();
        if (focusArea === 'video') {
          if (selectedIndex === currentVideos.length) {
            loadMoreVideos();
          } else if (currentVideos[selectedIndex]) {
            openVideo(currentVideos[selectedIndex]);
          }
        }
        break;
    }
  }

</script>

<svelte:window on:keydown={handleKeydown}/>

<div class="page-container">
  <header>
    <h1>맞춤 건강 정보</h1>
    <div class="category-buttons">
      {#each categories as category, index}
        <button 
          class="category-button" 
          class:selected={selectedCategory === category && focusArea === 'category'}
          on:click={() => selectCategory(category)}
        >
          {category || ''}
        </button>
      {/each}
    </div>
  </header>

  <section class="video-section">
    <div class="video-scroll" bind:this={scrollContainer}>
      <div class="video-container">
        {#each Array.isArray(videos[selectedCategory]) ? videos[selectedCategory] : [] as video}
          <div 
            class="video-card" 
            on:click={() => openVideo(video)}
          >
            <div class="thumbnail-wrapper">
              <img 
                src={video.snippet.thumbnails.high.url} 
                alt={video.snippet.title}
                class="thumbnail"
              />
              <div class="play-overlay">
                <div class="play-button">▶</div>
              </div>
            </div>
            <div class="video-info">
              <h3 class="video-title">{video.snippet.title}</h3>
              <p class="channel-title">{parseDuration(video.duration)}</p>
            </div>
          </div>
        {/each}
        {#if pageTokens[selectedCategory]}
          <button 
            class="load-more-button"
            on:click={loadMoreVideos}
            disabled={isLoadingMore}
          >
            {isLoadingMore ? '로딩 중...' : '더 보기'}
          </button>
        {/if}
      </div>
    </div>
  </section>

  {#if showModal}
    <div class="modal-overlay" on:click={closeModal}>
      <div class="modal-content" on:click|stopPropagation>
        <button class="close-button" on:click={closeModal}>×</button>
        <iframe
          src="https://www.youtube.com/embed/{selectedVideo.id.videoId}?autoplay=1"
          title={selectedVideo.snippet.title}
          allowfullscreen
        ></iframe>
      </div>
    </div>
  {/if}
</div>

<style>
  /* 페이지 컨테이너 스타일 */
  .page-container {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 20px;
    padding-left: 250px;
    box-sizing: border-box;
    position: fixed;  /* 추가 */
    top: 0;          /* 추가 */
    left: 0;         /* 추가 */
  }
  header {
    text-align: center;
    margin-bottom: 40px;
  }

  h1 {
    font-size: 2.5em;
    color: #333;
    margin-bottom: 30px;
  }

  .category-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-bottom: 30px;
    flex-wrap: wrap;
  }

  .category-button {
    font-size: 1.2em;
    padding: 10px 20px;
    background-color: white;
    border: 2px solid #ff9900;
    color: #ff9900;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 25px;
  }

  .category-button.selected {
    background-color: #ff9900;
    color: white;
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  }

  .video-section {
    margin-top: auto;
    width: 100%;
  }

  .video-scroll {
    width: 100%;
    overflow-x: auto;
    padding: 20px 0;
    margin-right: -20px;
  }

  .video-container {
    display: flex;
    gap: 20px;
    padding: 0 20px;
    padding-right: 40px;
    width: max-content;
  }

  .video-card {
    flex: 0 0 500px;
    height: 600px;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, outline 0.3s ease;
    cursor: pointer;
  }

  .video-card.selected {
    outline: 6px solid #ff9900;
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.2);
  }

  .load-more-button {
    flex: 0 0 100px;
    height: 100px;
    margin: auto 0;
    border-radius: 50%;
    background-color: white;
    border: 2px solid #ff9900;
    color: #ff9900;
    font-size: 1.2em;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .load-more-button:hover,
  .load-more-button.selected {
    background-color: #ff9900;
    color: white;
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  }

  .load-more-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .thumbnail-wrapper {
    position: relative;
    width: 100%;
    padding-top: 56.25%;
    overflow: hidden;
  }

  .thumbnail {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .play-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.3);
    opacity: 0;
    transition: opacity 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .video-card:hover .play-overlay,
  .video-card.selected .play-overlay {
    opacity: 1;
  }

  .play-button {
    font-size: 48px;
    color: white;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }

  .video-info {
    padding: 20px;
    height: calc(100% - 56.25% - 40px);
    overflow-y: auto;
  }

  .video-title {
    font-size: 30px;
    font-weight: 600;
    margin: 0 0 8px 0;
    line-height: 1.4;
    max-height: none;
    overflow: visible;
    white-space: normal;
  }

  .channel-title {
    font-size: 26px;
    color: #444;
    margin: 0;
    font-weight: 500;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal-content {
    width: 90%;
    max-width: 1200px;
    position: relative;
  }

  .modal-video-wrapper {
    position: relative;
    padding-bottom: 56.25%;
    height: 0;
  }

  .modal-video-wrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .close-button {
    position: absolute;
    top: -40px;
    right: -40px;
    font-size: 36px;
    color: white;
    background: none;
    border: none;
    cursor: pointer;
  }

  .loading {
    text-align: center;
    padding: 20px;
    color: #666;
  }

  /* 스크롤바 스타일링 */
  .video-scroll::-webkit-scrollbar {
    height: 8px;
  }

  .video-scroll::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .video-scroll::-webkit-scrollbar-thumb {
    background: #ff9900;
    border-radius: 4px;
  }

  .video-scroll::-webkit-scrollbar-thumb:hover {
    background: #ffc400;
  }
</style>
