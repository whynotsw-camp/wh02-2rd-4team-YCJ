<script>
  import { createEventDispatcher } from 'svelte';
  export let userInfo;
  const dispatch = createEventDispatcher();

  function handleBack() {
    dispatch('back');
  }

  async function handleConfirmData() {
    console.log('handleConfirmData');
  
    try {
      // BMI 계산 및 obesity_status 설정
      const bmi = calculateBMI(userInfo.weight, userInfo.height);
      console.log("bmi is " , bmi);
      // 고혈압 상태 설정
      const hypertensionStatus =
        userInfo.systolicBP >= 140 || userInfo.diastolicBP >= 90 ? '1' : '0';
      console.log("hyp is ", hypertensionStatus);
      // FastAPI에 데이터 전송

      const formData = new URLSearchParams({
        name: userInfo.name || '',
        age: (userInfo.age || 0).toString(),
        gender: userInfo.sex === '남자' ? '1' : '0', // 문자열 변환
        weight: (userInfo.weight || 0).toString(),
        height: (userInfo.height || 0).toString(),
        drinking_status: userInfo.drink === '예' ? '1' : '0',
        smoking_status: userInfo.smoke === '예' ? '1' : '0',
        obesity_status: (bmi.category >= 3).toString(), // BMI 기준 비만 상태
        fatigue_status: userInfo.fatigue === '예' ? '1' : '0',
        systolic_bp: (userInfo.systolicBP || 0).toString(),
        diastolic_bp: (userInfo.diastolicBP || 0).toString(),
        heart_rate: (userInfo.heartRate || 0).toString(),
        daily_steps: (userInfo.walking || 0).toString(),
        cholesterol_status: userInfo.cholesterol === '예' ? '1' : '0',
        daily_sleep: (userInfo.sleepTime || 0).toString(),
        hypertension_status: hypertensionStatus
      });

      console.log("Form Data: ", formData.toString());

      const response = await fetch('/api/user/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      console.log("response is ", response);

      if (response.ok) {
        const result = await response.json();
        console.log('User and detail data saved successfully:', result);

        // User ID를 디스패치 이벤트로 전달
        dispatch('confirm', {
            userId: result.user_id,
            detailId: result.detail_id
        });
      } else {
        console.error('Failed to save user and detail data:', response.statusText);
        console.log("response is ", response);
      }

    } catch (error) {
      console.error('Error saving user and detail data:', error);
    }
  }

  function calculateBMI(height, weight) {
    const bmi = weight / ((height / 100) ** 2); // BMI 계산
    let category;

    if (bmi < 18.5) {
      category = 1; // 저체중
    } else if (bmi >= 18.5 && bmi < 25) {
      category = 2; // 정상
    } else if (bmi >= 25 && bmi < 30) {
      category = 3; // 과체중
    } else {
      category = 4; // 비만
    }

    return { category };
  }

  function formatLabel(key) {
    const labels = {
      name: '성함',
      age: '연령',
      sex: '성별',
      weight: '몸무게',
      height: '키',
      sleepTime: '하루 수면시간',
      drink: '음주 여부',
      smoke: '흡연 여부',
      fatigue: '피로 여부',
      systolicBP: '수축기 혈압',
      diastolicBP: '이완기 혈압',
      heartRate: '심박수',
      walking: '하루 걸음 수',
      cholesterol: '콜레스테롤 과다 여부'
    };
    return labels[key] || key;
  }

  function formatValue(key, value) {
    if (value === null || value === undefined || value === '') {
      return '미입력';
    }
    if (key === 'sex') {
      return value === '1' ? '남자' : '여자';
    }
    if (['drink', 'smoke', 'fatigue', 'cholesterol'].includes(key)) {
      return value === '1' ? '예' : '아니오';
    }
    if (key === 'weight') {
      return `${value} kg`;
    }
    if (key === 'height') {
      return `${value} cm`;
    }
    if (key === 'sleepTime') {
      return `${value} 시간`;
    }
    if (key === 'walking') {
      const walkingLabels = {
        10000: '매우 많이 걷는다',
        8000: '꽤 많이 걷는다',
        7000: '보통 걷는다',
        5600: '조금 걷는다',
        3000: '거의 걷지 않는다'
      };
      return `${walkingLabels[value]} (${value} 걸음)`;
    }
    return value;
  }
</script>

<div class="info-confirm">
  <h2>입력하신 정보가 맞나요?</h2>
  
  <div class="info-list">
    {#each Object.entries(userInfo) as [key, value]}
      <div class="info-item">
        <span class="label">{formatLabel(key)}:</span>
        <span class="value">{formatValue(key, value)}</span>
      </div>
    {/each}
  </div>

  <div class="navigation">
    <button type="button" on:click={handleBack}>돌아가기</button>
    <button type="button" on:click={handleConfirmData}>확인</button>
  </div>
</div>

<style>
  .info-confirm {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }

  h2 {
    margin-bottom: 1em;
  }

  .info-list {
    text-align: left;
    margin-bottom: 1em;
    background: white;
    padding: 2em;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-width: 500px;
    width: 90%;
  }

  .info-item {
    margin-bottom: 0.8em;
    padding-bottom: 0.8em;
    border-bottom: 1px solid #eee;
  }

  .info-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }

  .label {
    font-weight: bold;
    margin-right: 0.5em;
    color: #666;
    min-width: 120px;
    display: inline-block;
  }

  .value {
    color: #333;
  }

  .navigation {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 300px;
    margin-top: 2em;
  }

  button {
    font-size: 1.2em;
    padding: 0.8em 1.5em;
    background-color: white;
    border: 2px solid #ff9900;
    color: #ff9900;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 5px;
    min-width: 120px;
  }

  button:hover {
    background-color: #ff9900;
    color: white;
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }
</style>
