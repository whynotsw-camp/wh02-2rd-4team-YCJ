<script>
	// Svelte의 기본 기능들을 가져옵니다
	import { createEventDispatcher, onMount } from 'svelte';

	// 이벤트 디스패처 생성 (부모 컴포넌트와의 통신을 위함)
	const dispatch = createEventDispatcher();
	// 출력할 전체 텍스트
	let text = "Fit For You에 오신 것을 환영합니다";
	// 현재까지 표시된 텍스트를 저장할 변수
	let displayText = "";
	// 현재 출력 중인 글자의 인덱스
	let currentIndex = 0;
	// 커서 표시 여부를 결정하는 상태 변수
	let showingCursor = false;

	// '시작하기' 버튼 클릭 시 실행되는 함수
	function handleStart() {
		dispatch('start');
	}

	// 컴포넌트가 마운트될 때 실행되는 함수
	onMount(() => {
		// 60ms 간격으로 글자를 하나씩 추가하는 타이머 설정
		const interval = setInterval(() => {
			if (currentIndex < text.length) {
				displayText += text[currentIndex];
				currentIndex++;
			} else {
				showingCursor = true;
				clearInterval(interval);
			}
		}, 60);

		// 컴포넌트가 언마운트될 때 타이머 정리
		return () => clearInterval(interval);
	});
</script>

<div class="background">
	<div class="welcome">
		<!-- 타이핑 효과와 커서를 포함한 제목 -->
		<h1 class="fade-in">{displayText}{#if showingCursor}<span class="cursor">_</span>{/if}</h1>
		<!-- 메인 이미지 -->
		<img src="static/main_page.png" alt="건강 관리 아이콘" class="welcome-image fade-in">
		<!-- 시작하기 버튼 -->
		<button on:click={handleStart}>시작하기</button>
	</div>
</div>

<style>
	/* 배경 이미지 설정 */
	.background {
		background-image: url('background.png');
		background-size: cover;
		background-position: center;
		min-height: 100vh;
		width: 100%;
		position: fixed;
		top: 0;
		left: 0;
	}

	/* 콘텐츠 중앙 정렬을 위한 컨테이너 스타일 */
	.welcome {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
	}

	/* 제목 스타일 */
	h1 {
		font-size: 3em;
		margin-bottom: 1em;
		min-height: 1.2em;
		opacity: 0;
	}

	/* 메인 이미지 스타일 */
	.welcome-image {
		width: 500px;
		height: auto;
		margin: 1em 0;
		opacity: 0;
	}

	/* 페이드인 애니메이션 클래스 */
	.fade-in {
		animation: fadeIn 1s ease-in forwards;
	}

	/* 페이드인 애니메이션 정의 */
	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	/* 버튼 기본 스타일 */
	button {
		font-size: 2.4em;
		padding: 0.8em 1.5em;
		background-color: white;
		border: 2px solid #ff9900;
		color: #ff9900;
		cursor: pointer;
		transition: all 0.3s ease;
		border-radius: 5px;
	}

	/* 버튼 호버 효과 */
	button:hover {
		background-color: #ffc400;
		color: white;
		transform: scale(1.05);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	/* 커서 스타일 */
	.cursor {
		animation: blink 1s infinite;
	}

	/* 커서 깜빡임 애니메이션 정의 */
	@keyframes blink {
		0% { opacity: 1; }
		50% { opacity: 0; }
		100% { opacity: 1; }
	}
</style>
