--__author__ = 'Lothilius'

on run {input, parameters}
	tell application "Terminal"
		activate
		if (the (count of the window) = 0) or ¬
			(the busy of window 1 = true) then
			tell application "System Events"
				keystroke "n" using command down
			end tell
		end if
		do script "ipython" in window 1
		do script "import pandas as pd" in window 1
		delay 1
		do script "data = pd.read_csv(\"" & (POSIX path of (input as string)) & "\")" in window 1
	end tell
	return input
end run
