// Page Loader Animation
window.addEventListener('load', function() {
    const loader = document.querySelector('.page-loader');
    setTimeout(function() {
        loader.classList.add('loader-hidden');
    }, 1000);
});

// +++++++++++++++++++++  FIRSRT PAGE ANIMATION ++++++++++++++++++++++++++

const girlIllustration=document.querySelector('#land-img');
const potLeft=document.querySelector('#pot_1');
const potRight=document.querySelector('#pot_2');
const girlsShadow=document.querySelector('.shadow');

/* Disabled scroll animation to fix image position glitch
window.addEventListener('scroll',()=>{
    let val=window.scrollY;
    girlIllustration.style.bottom=`${val}px`;
    potRight.style.bottom=`${val*0.7}px`;
    potLeft.style.bottom=`${val*0.7}px`;
    if(val<170){
        girlsShadow.style.width=`${val+160}px`;
    }
})
*/

// PAGE LINKING STUFF


const card1=document.querySelector('.card-1');
const card2=document.querySelector('.card-2');
const card3=document.querySelector('.card-3');
const card4=document.querySelector('.card-4');
const chatBotPageTakingBtn=document.querySelector('#chat-bot-page-portal-btn');


if (card1) {
    card1.addEventListener('click',()=>{
        window.location.href="otherHTML/food.html";
    })
}

if (card2) {
    card2.addEventListener('click',()=>{
        window.location.href="otherHTML/exercise.html";
    })
}

if (card3) {
    card3.addEventListener('click',()=>{
        window.location.href="#section-3";
    })
}

if (card4) {
    card4.addEventListener('click',()=>{
        window.location.href="otherJS/carGame/games.html";
    })
}

if (chatBotPageTakingBtn) {
    chatBotPageTakingBtn.addEventListener('click',()=>{
        window.location.href="otherHTML/chatBot.php";
    })
}



// +++++++++++++++++++++++++++ ANIMATION STUFFS


const cards=document.querySelectorAll('.card');


let options ={
    root: null,
    rootMargin:'200px',
    threshold:0.15
}

let observer= new IntersectionObserver((entries,observe)=>{

    entries.forEach((entry)=>{

        if(entry.isIntersecting){
            entry.target.classList.add('appear');
        }
    })
},options)


cards.forEach((card)=>{
    observer.observe(card);
})



// SMALLCARD ANIMATIONS++++++++++ 

const smallCrads=document.querySelectorAll('.more-card');


let smallCradOptions={
    root: null,
    rootMargin:'0px',
    threshold:0
}


let smallCardobserver = new IntersectionObserver((entries, observe) => {

    entries.forEach((entry) => {

        if (entry.isIntersecting) {
            entry.target.classList.add('appear');
        }

    });

}, smallCradOptions);


smallCrads.forEach((card, index) => {

    const delay = 300 + (index * 200);

    card.style.transitionDelay = `${delay}ms`;

    smallCardobserver.observe(card);

});



window.addEventListener('scroll',()=>{
    if (window.scrollY === 0) {
        cards.forEach((card)=>{
            card.classList.remove('appear');
        })

        smallCrads.forEach((card)=>{
            card.classList.remove('appear');
        })
    }
})


// //// Page reload

const logo=document.querySelector('.logo');

if (logo) {
    logo.addEventListener('click',()=>{
        window.location.reload();
    })
}




// ///////// ATTRIBUTION CONT ON FOOTER

const attributeText=document.querySelector('.attribute-text');
const attributeCont=document.querySelector('.actual-author-contribution-cont');
const cross=document.querySelector('#close-attributions');

function hideAttributeModal() {
    if (attributeCont) {
        attributeCont.style.top="500px";
        attributeCont.style.opacity="0";
    }
}

if (attributeText && attributeCont) {
    attributeText.addEventListener('click',()=>{
        attributeCont.style.top="50px";
        attributeCont.style.opacity="1";
    })
}

if (cross) {
    cross.addEventListener('click', hideAttributeModal);
}

if (attributeCont) {
    attributeCont.addEventListener('click', (event) => {
        if (event.target === attributeCont) {
           hideAttributeModal();
        }
    });
}


if (document && attributeCont && attributeText) {
    document.addEventListener('click', (event) => {
        if (attributeCont.style.opacity === '1' &&
            !attributeCont.contains(event.target) &&
            !attributeText.contains(event.target)) {
            hideAttributeModal();
        }
    });
}