*This information is also available as a video tutorial: <a class="external" rel="noreferrer nofollow" target="_blank" href="https://www.youtube.com/watch?v=WS-mRodmsMs">Workspaces</a>*

Workspaces are a way to upload data and visualize it without the context of a study. In general, we'd recommend that you organize your data into studies so that we can assign rich metadata to it and provide it to visitors. However, workspaces could be a good solution when:

- You have data that is not organized yet and would like to explore it or share it with others.
- You would like to try out our visualization or modeling interfaces to learn what tools you have available.
- You are experimenting with the mGrowthDB [API](https://mgrowthdb.readthedocs.io/en/latest/api.html) and would like to use the application as a convenient visualization interface.

Each workspace belongs to a single user and is identified by their ORCID and by a name. Each user has a default workspace labeled "default" that they can't delete, but they can create other ones. Workspaces are private by default, but could be made public so that anyone with a link can access them.

## Direct upload

<div class="image-container" style="width: 40%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        src="/static/images/help/workspaces/direct_upload_1.png"
        title="Upload form template" />
    <img
        src="/static/images/help/workspaces/direct_upload_2.png"
        title="Upload form with an attached file with error columns" />
    <img
        src="/static/images/help/workspaces/direct_upload_3.png"
        title="Uploaded data example" />
</div>

The most basic way of using workspaces is to click on the "Workspaces" link in the sidebar menu and you'll be placed on a page that is unique to your user. You can use a form on the right-hand side of the page to upload data CSVs and, optionally, describe the data that is contained in them.

The form always expects the first column to contain time values and each other column to be measurement values. It could be the case that your data includes error values that you'd like to plot as error bars. In that case, tick the "**Include error columns**" checkbox and the columns will be interpreted as pairs of value and error columns. Once you attach a file, you should be able to see a preview of the detected columns with annotations of *[Time]*, *[Value]*, or *[Error]* depending on how the system interprets them.

You can find example data at the bottom of the form that you can download and experiment with. You can also simply try out different data files and see how they are interpreted. You can always clear the contents of the workspace, since it's meant to be somewhat temporary.

Once you upload the data, it should show up on the left-hand side under the "**Direct upload**" section. You can annotate the data by filling in the form below the upload interface. You can choose whether this is meant to be **observational measurements** or **model predictions**. You can describe whether the data is growth measurements of a **community** or a **strain**, or **metabolite** measurements over time. If you choose the measurement subject type, you'll also get appropriate options about the units the data is uploaded in.

The metadata form is optional. You can upload the CSV and then simply plot the data and examine it. However, if you fill it in, you can fit models to cell growth data and you can compare it with other data from published studies with compatible units. You can also complete the metadata on a case by case basis after uploading by pressing the "Edit" button on a data trace and updating the form.

## API

TODO

## Visualizing and fitting models

TODO

## Creating and publishing workspaces

TODO
