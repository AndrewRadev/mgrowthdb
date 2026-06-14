*This information is also available as a video tutorial: <a class="external" rel="noreferrer nofollow" target="_blank" href="https://www.youtube.com/watch?v=WS-mRodmsMs">Workspaces</a>*

Workspaces are a way to upload data and visualize it without the context of a study. In general, we'd recommend that you organize your data into studies with rich metadata. However, workspaces could be a good solution when:

- You have data that is not organized yet and would like to explore it or share it with others.
- You would like to try out our visualization or modeling interfaces to learn what tools you have available.
- You are building an application with the mGrowthDB [API](https://mgrowthdb.readthedocs.io/en/latest/api.html) and would like to use the web interface for its visualization capabilities.

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

The most basic way of using workspaces is to click on the "Workspaces" link in the sidebar menu which will place you on a page that is unique to your user. You can use a form on the right-hand side of the page to upload data CSVs and, optionally, describe the data that is contained in them.

The form always expects the first column to contain time values and each other column to be measurement values. It could be the case that your data includes error values that you'd like to plot as error bars. In that case, tick the "**Include error columns**" checkbox and the data will be interpreted as pairs of value and error columns. Once you attach a file, you should be able to see a preview of the detected columns with annotations of *[Time]*, *[Value]*, or *[Error]* depending on how the system interprets them.

You can find example data at the bottom of the form that you can download and experiment with. You can also simply try out different data files and see how they are interpreted. You can always clear the contents of the workspace, since it's meant to be somewhat temporary.

Once you upload the data, it should show up on the left-hand side under the "**Direct upload**" section. Each value or value-error pair will be extracted into a separate data trace. You can annotate the traces by filling in the form below the upload interface. You can choose whether this is meant to be **observational measurements** or **model predictions**. You can describe whether the data is growth measurements of a **community** or a **strain**, or **metabolite** measurements. If you choose the measurement subject type, you'll also get appropriate options about the units the data is uploaded in.

The metadata form is optional. You can upload the CSV and then simply plot the data and examine it. However, if you fill it in, you can fit models to cell growth data and you can compare it with measurements from published studies with compatible units. You can also complete the metadata on a case by case basis after uploading by pressing the "Edit" button on a data trace and updating the form.

## API

Apart from uploading data CSVs, you can also populate your workspace with data through the programmatic API. This process is described in detail in the developer documentation: [API/workspaces](https://mgrowthdb.readthedocs.io/en/latest/api.html#workspaces).

When you push data through the API, it will show up on the workspace page in the "API data" section. It will also become available in charts in the "Visualize" tab. You can fit models to API-pushed data, but bear in mind that pushing data again will delete all the existing API entries (and their fitted models) and replace them with the sent data. This is done to avoid accidentally uploading the same datasets over and over again if running the push in a script that is invoked multiple times.

If you'd like to retain the previously-pushed data and push a new batch of entries to the workspace, you can pass an `?append=1` query parameter.

## Visualizing and fitting models

<div class="image-container" style="width: 40%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        src="/static/images/help/workspaces/visualize_1.png"
        title="Direct upload data source" />
    <img
        src="/static/images/help/workspaces/visualize_2.png"
        title="Compare data source" />
</div>

Clicking on the "Visualize" tab brings you to a page where you can select uploaded data traces and plot them on a chart. The mechanics of using the chart are similar to other charts on the website and we recommend reading the documentation on [study pages](/help/study-pages/) to learn how to manipulate them. On this page, you can visualize data traces from the API, and also from studies by using the "Compare" interface. Any data that you've collected by clicking on its "compare" button will show up on this page under the "Compare" data source. That way, you can plot your own data along with existing studies.

Clicking on the "Fit models" tab brings you to an interface that is similar to the model-fitting interface described in the [study pages](/help/study-pages/) documentation. Note that you can only fit models on uploaded data that has been marked as "observational" and measuring either community-level or strain-level measurements, since at this time, the available models are meant for microbial growth data.

Any models fitted on uploaded data traces will be shown visually attached to them, as seen in the screenshots. You can always upload model predictions in the "Direct upload" sections as well, and compare them with the fits generated from the application.

## Creating and sharing workspaces

Workspaces are meant to be a somewhat temporary storage for data. By default, a workspace is private to your user and nobody can visit the URL. You can make a workspace public by clicking on the "Publish" button in the top right of the page:

<p>
    <div style="width: 100%; text-align: center">
    <img style="width: 60%; margin: 0 auto;" title="Publishing" src="/static/images/help/workspaces/publishing_1.png" />
    </div>
</p>

<div class="image-container" style="width: 40%; float: right; margin-left: 20px; margin-top: 20px;">
    <img
        src="/static/images/help/workspaces/publishing_2.png"
        title="Creating or deleting workspaces" />
</div>

Once a workspace is public, you can copy the URL of the page and simply send it to other people to interact with. They will **not** be able to modify the workspace or upload new data to it, only read it. They will be able to download the data traces and visualize them. They will not be able to fit models, since that process creates new records that live in the workspace.

You can change the current workspace you're looking at by changing the dropdown at the top right of the page. If you'd like to create a new workspace for a particular purpose (for instance, for sharing a specific set of data files with other lab members), you can use the form in the bottom right of the upload page to create a workspace with a specific name. Every user has one default workspace named "default", but can create others. You can also delete a workspace or clear its items to re-upload data. You cannot delete the "default" workspace. If you try to create a workspace with a name that already exists, the page will simply switch to it instead.

If you'd like to share the "Visualize" page of your workspace, you can just send the URL of the page, but it's also possible to build a particular chart and copy the "Link to this page" link below the chart. This will give you a URL to this particular configuration of chart traces.
