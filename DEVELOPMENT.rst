OPEN ISSUES:

1. Openslides needs to provide some plugin hooks into agenda and motions.

Currently, I replace the following openslides files with the ones provided in this package:
agenda/static/js/agenda/site.js
agenda/static/templates/agenda/item-detail.html
motions/static/js/motions/site.js

Search for "FIXME JW" in those files to find the currently provided hooks.

2. Form to add keypads by range

3. Projector message "Vote now"

4. Motion slide with seating plan and vote status shown while votecollector is running

5. Projector message with instructions on how to get on the speaker list when votecollector is running

6. Change seat number (AP 1.3)

7. Translation

8. Review setup.py

Search for TODO to find all the open issues in the source code

http://files.softwein.de/votecollector-dev.zip

JW, 2016-09-29



TODO for me:

1. Add seating plan projector element and button to project it during motion poll voting.
2. Added new seating plan view with bootbox to update the description of single seats.  -- Done..
3. Add site view with all single votes. -- Done without templating.
4. Added button to delete names from single votes (anonymous votes) of motion poll voting.
5. Added button for PDF with all single votes of a motion poll voting.
6. Calculate maxXAxis and maxYAxis.

NJ, 2016-08-20
