
var win = Titanium.UI.currentWindow;
win.setBarColor('#d70000');
win.titleImage = '../images/scienceNav.png';
win.hideNavBar();
win.backgroundImage = "../images/sci-mob-bg.png";

//elements have been coded in order they're displayed

var scienceImageView = Titanium.UI.createImageView({
	url:'../images/mob-sci-logo-sm.png',
	width:122,
	height:78,
	top:12
});




var buttonNews = Titanium.UI.createButton({
	title:'Latest News',
	height:46,
	width:258,
	font:{fontSize:20,fontWeight:'bold'},
	backgroundImage:'../images/mob-btn-main-off.png',
	backgroundSelectedImage:'../images/mob-btn-main-on.png',
	top:102

});

var buttonCareers = Titanium.UI.createButton({
	title:'Careers',
	height:46,
	width:258,
	font:{fontSize:20,fontWeight:'bold'},	
	backgroundImage:'../images/mob-btn-main-off.png',
	backgroundSelectedImage:'../images/mob-btn-main-on.png',
	top:160
});


var decoImageView = Titanium.UI.createImageView({
	url:'../images/mob-deco-swish.png',
	width:321,
	height:25,
	top:233
});


/*
var magazineLabel = Titanium.UI.createLabel({
	text:"Science",
	textAlign:"center",
	top:10,
	font:{fontSize:22,fontWeight:'bold'},
	color:'#fff',
	shadowOffset:{x:5,y:5}
	
})
*/



var images = [];
	images[0]='../images/mob-test-cover-sig.png';
	images[1]='../images/mob-test-cover.png';
	images[2]='../images/mob-test-cover-stm.png';







var sliderView = Titanium.UI.createCoverFlowView({
	width:320,
    //cannot have "height" property, as it messes alignment all up
	top:220,
	left:0,
	right:0,
	images:images,
	backgroundColor:'transparent'
});



/*
var overlay = Titanium.UI.createImageView({
	url:'../images/_alignment.png',
	width:320,
	height:480,
	top:0,
	zIndex:-1
});
*/

//win.add(overlay);
win.add(sliderView); //slider MUST go here, before the others. Otherwise it will cover the rest of the buttons
win.add(scienceImageView);
win.add(buttonNews);
win.add(buttonCareers);
win.add(decoImageView);
//win.add(magazineLabel);




//
// Events
//





/*work around for selected problem:
setTimeout(function(){
    sliderView.selected = 1;
},200);
*/

win.addEventListener('focus', function()
{
setTimeout(function(){
    sliderView.selected = 1;
},200);
});




buttonNews.addEventListener('click',function()
{
	var newsWin = Titanium.UI.createWindow({
		url:'../page_windows/news-main.js',
		title:'Latest News',
		//backgroundImage:'../images/sci-mob-bg.png'
		});

	Titanium.UI.currentTab.open(newsWin,{animate:true});
});



buttonCareers.addEventListener('click',function()
{
	var careersWin = Titanium.UI.createWindow({
		url:'../page_windows/careers-main.js',
		title:'Careers'
		});

	Titanium.UI.currentTab.open(careersWin,{animate:true});
});



sliderView.addEventListener('click',function(e)
{
	
	if(e.index==0){
		var newWin = Titanium.UI.createWindow({
		url:'../page_windows/signaling-main.js',
		title:'Signaling'
		});

		Titanium.UI.currentTab.open(newWin,{animate:true});
	}
	
	if(e.index==1){
		var newWin = Titanium.UI.createWindow({
		url:'../page_windows/science-main.js',
		title:'Science'
		});

		Titanium.UI.currentTab.open(newWin,{animate:true});
	}
	
	if(e.index==2){
		var newWin = Titanium.UI.createWindow({
		url:'../page_windows/stm-main.js',
		title:'STM'
		});

		Titanium.UI.currentTab.open(newWin,{animate:true});
	}
	
});


/*

sliderView.onload =function(e){
	e.index=1;
}*/

/*
sliderView.addEventListener('change',function(e)
{
	if(e.index==0){
		magazineLabel.text="Science";
	}
	if(e.index==1){
		magazineLabel.text="Science Signaling";
	}
	if(e.index==2){
		magazineLabel.text="Science Translational\nMedicine";
	}
	//Titanium.API.info("image changed: "+e.index+', selected is '+view.selected);	
});

*/