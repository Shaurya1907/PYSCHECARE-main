



//+++++++++++++++++++++++++++++++++HAMBURGER MENU+++++++++++++=++++++++++++++++++++++++



const hamburger=document.querySelector('.hamburger, .hamBurger');


const line1=document.querySelector('.line1');
const line2=document.querySelector('.line2');
const line3=document.querySelector('.line3');
const midLine1=document.querySelector('.mid-line1');
const midLine2=document.querySelector('.mid-line2');

const mobileNav=document.querySelector('#mobile-nav');

const mobileNavList=document.querySelectorAll('.mobile-view-list');


if (hamburger) {
    hamburger.addEventListener('click',()=>{
        if (line1) line1.classList.toggle('changetheline1');
        if (line3) line3.classList.toggle('changetheline3');

        if (midLine1) midLine1.classList.toggle('changeMidLine1');
        if (midLine2) midLine2.classList.toggle('changeMidLine2');

        if (mobileNav) mobileNav.classList.toggle('show-nav');
    });
}


mobileNavList.forEach((list)=>{
    list.addEventListener('click',()=>{
        if (mobileNav) mobileNav.classList.remove('show-nav');

        if (line1) line1.classList.toggle('changetheline1');
        if (line3) line3.classList.toggle('changetheline3');
    
        if (midLine1) midLine1.classList.toggle('changeMidLine1');
        if (midLine2) midLine2.classList.toggle('changeMidLine2');
    })
})