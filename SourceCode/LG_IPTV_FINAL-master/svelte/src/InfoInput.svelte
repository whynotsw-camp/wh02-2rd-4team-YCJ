<script>
	import { createEventDispatcher, onMount } from 'svelte';
  
	const dispatch = createEventDispatcher();
  
	let currentStep = 0;
	let userInfo = {
	  name: '',
	  age: '',
	  sex: '',
	  weight: '',
	  height: '',
	  sleepTime: '',
	  drink: '',
	  smoke: '',
	  fatigue: '',
	  systolicBP: '',
	  diastolicBP: '',
	  heartRate: '',
	  walking: '',
	  cholesterol: ''
	};
  
	let displayText = '';
	let currentIndex = 0;
	let showingCursor = false;
	let errorMessage = '';
  
	const steps = [
	  { field: 'name', label: '성함이 어떻게 되시나요?', type: 'text', required: true },
	  { field: 'age', label: '연세가 어떻게 되시나요?', type: 'number', required: true },
	  { field: 'sex', label: '성별을 선택해 주세요', type: 'select', options: ['남자', '여자'], required: true },
	  { field: 'weight', label: '몸무게는 몇 kg이신가요?', type: 'number', step: '0.1', required: true },
	  { field: 'height', label: '키는 몇 cm이신가요?', type: 'number', step: '0.1', required: true },
	  { field: 'sleepTime', label: '하루에 몇 시간 주무시나요?', type: 'number', step: '0.5', required: true },
	  { field: 'drink', label: '술을 드시나요?', type: 'select', options: ['예', '아니오'], required: true },
	  { field: 'smoke', label: '담배를 피우시나요?', type: 'select', options: ['예', '아니오'], required: true },
	  { field: 'fatigue', label: '평소에 피로감을 느끼시나요?', type: 'select', options: ['예', '아니오'], required: true },
	  { field: ['systolicBP', 'diastolicBP'], label: '혈압은 어떻게 되시나요?', type: 'number', required: false },
	  { field: 'heartRate', label: '심장박동수는 어떻게 되시나요?', type: 'number', required: false },
	  { field: 'walking', label: '평소에 걷기 운동을 얼마나 하시나요?', type: 'select', options: ['매우 많이 걷는다', '꽤 많이 걷는다', '보통 걷는다', '조금 걷는다', '거의 걷지 않는다'], required: false },
	  { field: 'cholesterol', label: '콜레스테롤이 높다고 들어보셨나요?', type: 'select', options: ['예', '아니오'], required: false }
	];
  
	// 타이핑 효과 초기화
	onMount(() => startTyping());
  
	$: if (steps[currentStep]) {
	  clearTypingEffect();
	  startTyping();
	}
  
	function clearTypingEffect() {
	  displayText = '';
	  currentIndex = 0;
	  showingCursor = false;
	}
  
	function startTyping() {
	  const text = steps[currentStep].label;
	  const interval = setInterval(() => {
		if (currentIndex < text.length) {
		  displayText = text.substring(0, currentIndex + 1);
		  currentIndex++;
		} else {
		  showingCursor = true;
		  clearInterval(interval);
		}
	  }, 60);
	  return () => clearInterval(interval);
	}
  
  
	function handleNext() {
	  if (isValidInput()) {
		errorMessage = '';
		if (currentStep < steps.length - 1) {
		  currentStep++;
		} else {
			print(userInfo);
		  dispatch('finish', userInfo);
		}
	  }
	}
  
	function handleBack() {
	  errorMessage = '';
	  if (currentStep > 0) {
		currentStep--;
	  } else {
		dispatch('goToWelcome');
	  }
	}
  
	// 건너뛰기 기능 추가
	function handleSkip() {
	  errorMessage = '';
	  if (!steps[currentStep].required) {
		if (Array.isArray(steps[currentStep].field)) {
		  steps[currentStep].field.forEach(field => {
			userInfo[field] = null;
		  });
		} else {
		  userInfo[steps[currentStep].field] = null;
		}
		if (currentStep < steps.length - 1) {
		  currentStep++;
		} else {
		  dispatch('finish', userInfo);
		}
	  }
	}
  
	// 유효성 검증 로직 추가
	function isValidInput() {
	  const currentStepInfo = steps[currentStep];
	  if (Array.isArray(currentStepInfo.field)) {
		const systolic = userInfo.systolicBP;
		const diastolic = userInfo.diastolicBP;
		if ((systolic && !diastolic) || (!systolic && diastolic)) {
		  errorMessage = '수축기 혈압과 이완기 혈압을 모두 입력해주세요.';
		  return false;
		}
	  } else {
		const value = userInfo[currentStepInfo.field];
		if (currentStepInfo.required && !value) {
		  errorMessage = `${currentStepInfo.label}을(를) 입력해주세요.`;
		  return false;
		}
	  }
	  return true;
	}
  
	// 선택 항목 처리 추가
	function handleSelect(option) {
	  const currentField = steps[currentStep].field;
	  if (currentField === 'walking') {
		const walkingValues = {
		  '매우 많이 걷는다': 10000,
		  '꽤 많이 걷는다': 8000,
		  '보통 걷는다': 7000,
		  '조금 걷는다': 5600,
		  '거의 걷지 않는다': 3000
		};
		userInfo[currentField] = walkingValues[option];
	  } else {
		userInfo[currentField] = option;
	  }
	}
  
	// 입력 데이터 처리 추가
	function handleInput(event) {
	  if (steps[currentStep].field === 'name') {
		event.target.value = event.target.value.replace(/[^가-힣a-zA-Z\s]/g, '');
	  }
	}
  </script>
  
  <div class="background">
	<div class="info-input">
		<div class="question-container">
			<h2>{displayText}{#if showingCursor}<span class="cursor">_</span>{/if}</h2>
		</div>
		
		{#if errorMessage}
			<p class="error">{errorMessage}</p>
		{/if}
		
		{#if steps[currentStep].type === 'select'}
	<!-- 걷기 옵션과 일반 선택 항목 처리를 모두 포함 -->
		<div class="button-group">
			{#each steps[currentStep].options as option}
				<button 
					class:selected={userInfo[steps[currentStep].field] === (steps[currentStep].field === 'walking' ? 
						Object.values({
							'매우 많이 걷는다': 10000,
							'꽤 많이 걷는다': 8000,
							'보통 걷는다': 7000,
							'조금 걷는다': 5600,
							'거의 걷지 않는다': 3000
						})[steps[currentStep].options.indexOf(option)] : option)}
					on:click={() => handleSelect(option)}
				>
					{option}
				</button>
			{/each}
		</div>

		<!-- <div class="button-group">
			{#each steps[currentStep].options as option}
				<button 
					class:selected={userInfo[steps[currentStep].field] === option}
					on:click={() => handleSelect(option)}
				>
					{option}
				</button>
			{/each} 
		</div>-->
		{:else if Array.isArray(steps[currentStep].field)}
			<div class="input-group">
				<label>
					수축기 혈압:
					<input 
						type="number"
						bind:value={userInfo.systolicBP}
						required={steps[currentStep].required}
						on:input={() => userInfo = {...userInfo}}
					>
				</label>
				<label>
					이완기 혈압:
					<input 
						type="number"
						bind:value={userInfo.diastolicBP}
						required={steps[currentStep].required}
						on:input={() => userInfo = {...userInfo}}
					>
				</label>
			</div>
		{:else if steps[currentStep].type === 'text'}
			<input 
				type="text"
				bind:value={userInfo[steps[currentStep].field]}
				required={steps[currentStep].required}
				on:input={handleInput}
			>
		{:else if steps[currentStep].type === 'number'}
			<input 
				type="number"
				bind:value={userInfo[steps[currentStep].field]}
				step={steps[currentStep].step}
				required={steps[currentStep].required}
				on:input={handleInput}
			>
	{/if}


		<div class="navigation">
			<button on:click={handleBack}>뒤로가기</button>
			{#if !steps[currentStep].required}
				<button on:click={handleSkip}>건너뛰기</button>
			{/if}
			<button type="button" on:click={handleNext}>
				{currentStep === steps.length - 1 ? '확인' : '다음'}
			</button>
		</div>
	</div>
</div>


<style>
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

	.info-input {
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: flex-start;
			min-height: 100vh;
			padding-top: 2em;
	}

	.question-container {
			width: 100%;
			text-align: left;
			padding: 2em;
			margin-bottom: 2em;
	}

	h2 {
			position: relative;
			left: 20px;
			top: -100px;
			font-size: 5em;
			color: rgb(0, 0, 0);
			line-height: 1.3;
			font-weight: 500;
	}

	input {
			font-size: 1.2em;
			padding: 0.5em;
			margin-bottom: 1em;
			border: 1px solid #ccc;
			border-radius: 5px;
			width: 100%;
			max-width: 300px;
	}

	.button-group {
			display: flex;
			justify-content: center;
			flex-wrap: wrap;
			gap: 1em;
			margin-bottom: 1em;
	}

	.button-group button {
			font-size: 1.2em;
			padding: 0.5em 1em;
			background-color: white;
			border: 2px solid #ff9900;
			color: #ff9900;
			cursor: pointer;
			transition: all 0.3s ease;
			border-radius: 5px;
	}

	.button-group button.selected {
			background-color: #ff9900;
			color: white;
	}

	.button-group button:hover {
			background-color: #ffc400;
			color: white;
			transform: scale(1.05);
			box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.navigation {
			display: flex;
			justify-content: space-between;
			width: 100%;
			max-width: 300px;
			gap: 1em;
	}

	.navigation button {
			font-size: 1.2em;
			padding: 0.5em 1em;
			background-color: white;
			border: 2px solid #ff9900;
			color: #ff9900;
			cursor: pointer;
			transition: all 0.3s ease;
			border-radius: 5px;
	}

	.navigation button:hover {
			background-color: #ffc400;
			color: white;
			transform: scale(1.05);
			box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.input-group {
			display: flex;
			flex-direction: column;
			align-items: flex-start;
			margin-bottom: 1em;
			width: 100%;
			max-width: 300px;
	}

	.input-group label {
			margin-bottom: 0.5em;
			width: 100%;
			color: white;
			text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
	}

	.error {
			color: #ff3333;
			margin-bottom: 1em;
			text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
	}

	.cursor {
			animation: blink 1s infinite;
	}

	@keyframes blink {
			0% { opacity: 1; }
			50% { opacity: 0; }
			100% { opacity: 1; }
	}
</style>
