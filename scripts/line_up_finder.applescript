#!/usr/bin/osascript
-- Double-click or run: osascript scripts/line_up_finder.applescript
-- Lines up CKD Dataset in Finder (list view, sorted by name).

set folderPath to POSIX file "/Users/md.shadmantahsin/Desktop/STUDY/Title Defence/CKD Dataset"

tell application "Finder"
	activate
	set targetFolder to folder folderPath
	open targetFolder
	delay 0.3
	set current view of front window to list view
	set iconOpts to icon view options of targetFolder
	tell iconOpts
		set arrangement to name
	end tell
	try
		clean up front window
	end try
end tell

display notification "CKD Dataset: list view + sorted by name" with title "Finder lined up"
