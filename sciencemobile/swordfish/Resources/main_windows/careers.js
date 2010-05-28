var win = Titanium.UI.currentWindow;
win.setBarColor('#d70000');

//set up elements
var textFieldOne = Titanium.UI.createTextField({
	color:'#336699',
	height:35,
	top:10,
	left:10,
	right:10,
//	width:250,
	borderStyle:Titanium.UI.INPUT_BORDERSTYLE_ROUNDED
});


var labelOne = Titanium.UI.createLabel({
	top:50,
	left:10,
	width:300,
	color:'#777',
	height:'auto',
	font:{fontSize:13},
	text:'Type your search phrase here then click \"Search\". You can search by location, field, or keyword\n\nTop 10 results are shown. For more results, visit http://sciencecareers.sciencemag.org'
});


var goSearch = Titanium.UI.createButton({
	top:150,
	height:40,
	width:200,
	title:'Search'
});

var alertBox = Titanium.UI.createAlertDialog({
	title:'No search results',
	message:'There were no search results. Please go back and try a different keyword'
});





win.add(textFieldOne);
win.add(labelOne);
win.add(goSearch);



//events




goSearch.addEventListener('click', function()
{

	
	// change pages
	
	var resultWin = Titanium.UI.createWindow({
			url:'careers_results.js',
			title:'Search Results'
		
		});
			
		//make variable available to resultWin 
		resultWin.search = textFieldOne.value;
		
		//format search result for resultWin. First change any pluses to spaces. Then make all spaces pluses
		resultWin.search = resultWin.search.replace("+", " ");
		resultWin.search = resultWin.search.replace(" ", "+");
		Titanium.UI.currentTab.open(resultWin,{animated:true}) //this gives the back button and stuff


		//resultWin.open({animated:true}) // this just opens a window with no nav
		
	
});





/* test outputs


textFieldOne.addEventListener('return',function(e)
{
	labelOne.text = 'return received, val = ' + e.value;
	textFieldOne.blur();
});
textFieldOne.addEventListener('focus',function(e)
{
	labelOne.text = 'focus received, val = ' + e.value;
});
textFieldOne.addEventListener('blur',function(e)
{
	labelOne.text = 'blur received, val = ' + e.value;	
});
textFieldOne.addEventListener('change', function(e)
{
	labelOne.text = 'change received, event val = ' + e.value + '\nfield val = ' + tf1.value;	
})

*/