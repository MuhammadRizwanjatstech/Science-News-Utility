// this sets the background color of the master UIView (when there are no windows/tab groups on it)
Titanium.UI.setBackgroundColor('#000');


var tabGroup = Titanium.UI.createTabGroup();

var win1 = Titanium.UI.createWindow({  
    url:'main_windows/home.js',
    tabBarHidden:true
});


var tab1 = Titanium.UI.createTab({  
    icon:'images/nothingyet.png',
    title:'About',
    window:win1,
    
});



tabGroup.addTab(tab1);  


tabGroup.addEventListener('open',function()
{
	// set background color back to white after tab group transition
	Titanium.UI.setBackgroundColor('#fff');
	//Titanium.UI.setBackgroundImage('../images/sci-mob-bg.png');
});

tabGroup.setActiveTab(1);
// open tab group with a transition animation
tabGroup.open({
	transition:Titanium.UI.iPhone.AnimationStyle.FLIP_FROM_LEFT
});






