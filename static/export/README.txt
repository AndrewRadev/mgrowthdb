This folder contains raw submission data for all studies uploaded to mGrowthDB. Each study data is located in a folder labeled with the form "SMGDBxxx" which represents the public identifier of the study. The same data is also available as a ZIP archive for easy downloading.

Each study folder contains three types of files:

- A "study_design.json" file which is a JSON that represents the metadata of the study. The specific format of that metadata may vary based on the code that handled the upload process at the time. It should be roughly similar, but there may be differences.
- Multiple CSV files that contain the observational data from the uploaded spreadsheet. Each CSV corresponds to a single sheet. These are stored in plain CSV format, since it's more space-efficient.
- A "changes.log" that stores data export events with timestamps. Data will be updated when a study is updated, or on a time-based schedule.

A copy of all the data is also located in the ZIP file "all_studies.zip" for maximum convenience if you need to get a full data dump.

Note that licensing information should be available in the "study_design.json" file in the "licensingUrl" field of the "study" object. In general, studies should be available under a CC-BY 4.0 license, but please make sure to respect any different licensing restrictions that you find in the metadata.
