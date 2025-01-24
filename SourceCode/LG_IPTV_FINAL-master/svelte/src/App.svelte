<script>
  import Welcome from './Welcome.svelte';
  import InfoInput from './InfoInput.svelte';
  import InfoConfirm from './InfoConfirm.svelte';
  import MainPage from './MainPage.svelte';
  
  let currentPage = 'welcome'; // 초기 페이지 설정
  let userInfo = {}; // 사용자 정보 저장
  let userId = null; // userId 저장
//  let detailId = null; // userId 저장

  // 페이지 전환 함수
  function startInfoInput() {
    currentPage = 'infoInput';
  }

  function finishInfoInput(event) {
    userInfo = event.detail; // 이벤트에서 전달된 사용자 데이터 저장
    currentPage = 'infoConfirm';
  }

  function goBack() {
    if (currentPage === 'infoConfirm') {
      currentPage = 'infoInput';
    }
  }

  function goToWelcome() {
    currentPage = 'welcome';
  }

  function goToMainPage(event) {
    userId = event.detail.userId;
    console.log('User ID set to:', userId); // 디버그용 로그 추가
    currentPage = 'mainPage';
  }

</script>

<main>
  {#if currentPage === 'welcome'}
    <Welcome on:start={startInfoInput} />
  {:else if currentPage === 'infoInput'}
    <InfoInput on:finish={finishInfoInput} on:goToWelcome={goToWelcome} />
  {:else if currentPage === 'infoConfirm'}
    <InfoConfirm {userInfo} on:back={goBack} on:confirm={goToMainPage} />
  {:else if currentPage === 'mainPage'}
    <MainPage {userId} />
  {/if}
</main>

<style>
  main {
    text-align: center;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  @media (min-width: 640px) {
    main {
      max-width: none;
    }
  }
</style>
