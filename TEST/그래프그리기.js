document.addEventListener('DOMContentLoaded', function() {
    const apartmentSelect = document.getElementById('apartment-select');
    const tradeTypeSelect = document.getElementById('trade-type-select');
    const searchBtn = document.getElementById('search-btn');
    const graphContainer = document.getElementById('graph-container');

    searchBtn.addEventListener('click', function() {
        const selectedApartment = apartmentSelect.value;
        const selectedTradeType = tradeTypeSelect.value;

        fetch('/data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                selected_apartment_name: selectedApartment,
                selected_trade_type: selectedTradeType
            })
        })
        .then(response => response.json())
        .then(data => {
            // 데이터를 받아서 그래프를 그리는 코드를 여기에 작성합니다.
            // 예를 들어, Chart.js 라이브러리를 사용할 수 있습니다.
        })
        .catch(error => console.error('Error:', error));
    });

    // 페이지 로드 시 아파트 목록을 가져오는 AJAX 요청을 수행할 수 있습니다.
});
