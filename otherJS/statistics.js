var alldata=[
    {
        label: 'United States',
        data: [0.33, 0.65, 3.45, 4.84, 2.04, 6.64],
        borderColor: '#00B7A8',
        borderWidth:2,
        tension:0,

    },
    {
        label: 'United Kingdom',
        data: [0.26, 1.09, 1.66, 4.12, 1.90, 4.65],
        borderColor: 'blue',
        borderWidth:2,
        tension:0,

    },
    {
        label: 'World',
        data: [0.25, 0.60, 0.94, 3.44, 1.40, 3.76],
        borderColor: '#1C2B2D',
        borderWidth:2,
        tension:0,
    }
];

const DEFAULT_COUNTRIES = ['United States', 'United Kingdom', 'World'];


// +++++++++++++++++++++++++ ADDING CHART ++++++++++++++++++++++++++++++++++++


var canvas = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(canvas, {
    type: 'line',
    data: {
        labels: [
                    'Schizophrenia',
                    'Bipolar disorder',
                    'Drug use disorders',
                    'Depression',
                    'Alcohol use disorders',
                    'Anxiety disorders'
                ],
        datasets: alldata,
    },
    options: {
        scales: {
            y: {
                ticks: {
                    
                    callback: function(value, index, values) {
                        return value + '%';
                    }
                }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
          },
    }
});




// ++++++++++++++++++++++++++ CHOOSE THE COUNTRY +++++++++++++++++++++++++++++++


const countryList=document.querySelector('#country-dropDown');


for(let i=0;i<data.length;i++){

    let option=document.createElement('option');

    option.textContent=data[i]['label'];

    option.setAttribute('value',`${data[i]['label']}`);


    countryList.appendChild(option);


}


// random Color picker

var colorHexCodeLetter=[1,2,3,4,5,6,7,8,9,0,'a','b','c','d','e','f'];

function randomColorPicker(){
    let colorString='#';
    for(let i=0;i<6;i++){
        let randomNum=Math.floor(Math.random()*colorHexCodeLetter.length);
        colorString+=`${colorHexCodeLetter[randomNum]}`
    }

    return colorString;
}




function updateChart(SelectedcountryName){


    for(let i=0;i<alldata.length;i++){
        if(SelectedcountryName===alldata[i]["label"]){
            return;
        }
    }
  

    for(let i=0;i<data.length;i++){

        if(data[i]['label']===SelectedcountryName){

            data[i]["borderColor"]=randomColorPicker();
            data[i].borderWidth= 2;
            data[i].tension=0;
            data[i].backgroundColor='transparent';

            alldata.push(data[i]);
            break;
        }

    }

    myChart.update();
    refreshRemoveDropdown();
}


function addCountry(countryName){
    let nameOfTheSelectedCountry=countryName.value

    if(nameOfTheSelectedCountry!="none"){
     
        updateChart(nameOfTheSelectedCountry);
        countryName.value = "none";
    }

}



// ++++++++++++++++++++++++++++ REMOVE COUNTRY FROM CHART +++++++++++++++++++++++++++


const removeCountryDropdown = document.querySelector('#remove-country-dropDown');

const errorBtn=document.querySelector('.error-btn');
const wholeChartCont=document.querySelector('.whole-staticstics-cont');
const errorMsgCont=document.querySelector('.error-msg-cont');


function refreshRemoveDropdown() {
    removeCountryDropdown.innerHTML = '<option value="none">Remove Country</option>';
    alldata.forEach(d => {
        if (!DEFAULT_COUNTRIES.includes(d.label)) {
            const option = document.createElement('option');
            option.textContent = d.label;
            option.setAttribute('value', d.label);
            removeCountryDropdown.appendChild(option);
        }
    });
}


function removeCountryFromChart(countryLabel){

    const index = alldata.findIndex(d => d.label === countryLabel && !DEFAULT_COUNTRIES.includes(d.label));
    if (index === -1) return;

    alldata.splice(index, 1);

    try{
        myChart.update();
        refreshRemoveDropdown();
    }catch(err){
        wholeChartCont.classList.add('blur-background');
        errorMsgCont.style.display="block";
    }

}


removeCountryDropdown.addEventListener('change', () => {
    const selected = removeCountryDropdown.value;
    if (selected !== "none") {
        removeCountryFromChart(selected);
    }
});

errorBtn.addEventListener('click',()=>{
    window.location.reload();
})











// ========== MOOD DASHBOARD CODE (Issue #320) ==========
let moodChart = null;
let distributionChart = null;
let allMoodData = [];

async function fetchMoodData(startDate, endDate) {
    try {
        const response = await fetch(/api/mood-history?start=\&end=\);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching mood data:', error);
        return generateSampleData();
    }
}

function generateSampleData() {
    const moods = ['Happy', 'Sad', 'Neutral', 'Excited', 'Anxious'];
    const data = [];
    const today = new Date();
    for (let i = 30; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        data.push({
            date: date.toISOString().split('T')[0],
            mood: moods[Math.floor(Math.random() * moods.length)],
            rating: Math.floor(Math.random() * 5) + 1
        });
    }
    return data;
}

function initCharts(data) {
    if (moodChart) moodChart.destroy();
    if (distributionChart) distributionChart.destroy();
    const dates = data.map(d => d.date);
    const ratings = data.map(d => d.rating);
    const moodLabels = [...new Set(data.map(d => d.mood))];
    const moodCounts = moodLabels.map(mood => data.filter(d => d.mood === mood).length);
    const ctx1 = document.getElementById('moodChart').getContext('2d');
    moodChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Mood Rating',
                data: ratings,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#4CAF50'
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' }, title: { display: true, text: 'Mood Trends Over Time' } },
            scales: { y: { min: 0, max: 5, ticks: { stepSize: 1 } } }
        }
    });
    const ctx2 = document.getElementById('distributionChart').getContext('2d');
    distributionChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: moodLabels,
            datasets: [{ data: moodCounts, backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'] }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Mood Distribution' } }
        }
    });
    updateSummaryStats(data);
}

function updateSummaryStats(data) {
    if (!data.length) return;
    let currentStreak = 0;
    for (let i = data.length - 1; i >= 0; i--) {
        if (data[i].rating >= 3) currentStreak++;
        else break;
    }
    const last7 = data.slice(-7);
    const avg = last7.reduce((s, d) => s + d.rating, 0) / last7.length;
    const moodCount = {};
    data.forEach(d => { moodCount[d.mood] = (moodCount[d.mood] || 0) + 1; });
    const mostCommon = Object.keys(moodCount).reduce((a, b) => moodCount[a] > moodCount[b] ? a : b);
    document.getElementById('current-streak').textContent = \\ days\;
    document.getElementById('weekly-avg').textContent = avg.toFixed(1);
    document.getElementById('most-common').textContent = mostCommon;
    document.getElementById('total-entries').textContent = data.length;
}

async function applyFilter() {
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;
    const data = await fetchMoodData(start, end);
    initCharts(data);
}

async function resetFilter() {
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    const data = await fetchMoodData('', '');
    initCharts(data);
}

document.addEventListener('DOMContentLoaded', async function() {
    const data = await fetchMoodData('', '');
    initCharts(data);
});
