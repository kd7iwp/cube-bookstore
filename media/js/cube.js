// Copyright (C) 2010  Trinity Western University

function toggleCBTogether()
{
    var inputlist = document.getElementsByTagName("input");
    checkboxCount = 0;
    checked = 0;
    for (i = 0; i < inputlist.length; i++)
    {
        if (inputlist[i].getAttribute("type") == 'checkbox')
        {
            checkboxCount++;
            if (inputlist[i].checked)
                checked++;
        }
    }
    if (checked > checkboxCount / 2)
        setCheckboxes(false);
    else
        setCheckboxes(true);
}



function setCheckboxes(set) 
{
    var inputlist = document.getElementsByTagName("input");
    for (i = 0; i < inputlist.length; i++) 
    {
        if ( inputlist[i].getAttribute("type") == 'checkbox' ) 
            inputlist[i].checked = set;
    }
}
