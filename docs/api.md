# API documentation

All published study data in the app should be downloadable at several different granularities:

1. Full study metadata and uploaded data spreadsheet for batch downloads under [/static/export](https://mgrowthdb.gbiomed.kuleuven.be/static/export/).
2. Export UI with selectable bioreplicates per-study under `/study/<studyId>/export`, for example: [SMGDB00000001/export](https://mgrowthdb.gbiomed.kuleuven.be/study/SMGDB00000001/export/)).
3. Fine-grained API access to entities through their ID or by performing a search.

The following document describes the third functionality, fine-grained API access. To learn more about the first two, take a look at the user documentation in the help files in the "[Downloading Data](https://mgrowthdb.gbiomed.kuleuven.be/help/downloading-data/)" topic.

For the following examples, we'll use curl to demonstrate responses. We'll use a `$ROOT_URL` that could be set to your localhost installation, or could be the public database:

```bash
export ROOT_URL="https://mgrowthdb.gbiomed.kuleuven.be"
```

The JSON output will be formatted for readability and in some places, truncated with a message like `"[...N more entries...]"`. There will be a general "output structure" description that describes the general shape of the JSON with the types of its fields.

Requests for specific global identifiers like `SMGDB00000001` or `EMGDB000000026` should work for you as well, so you should be able to replicate them by running them in the console. NCBI IDs and ChEBI IDs should also work for you. However, other numeric ids may be different, since updates to the underlying data might force them to be recreated. Try these out by fetching a specific study or experiment and picking bioreplicate ID or measurement context ID from the public entity's metadata.

## General principles

There are two types of results from the API:

- Metadata returned as JSON
- Measurement data returned in CSV format

The JSON endpoints always end in `.json` and the CSV ones end in `.csv`. A single entity might be downloadable in either format if you simply change the suffix. Explore the specific examples below.

The `measurementTimeUnits` key describes what time units measurements will be fetched in from the CSV endpoints. Right now, the API will always return time in hours ("h"), but this might be a configurable option later. For the moment, you can consider this an informational key, rather than something specific to the particular study or experiment.

Successful results will be returned with an HTTP status code of `200`. A request that somehow doesn't fit the requirements of the API will have a response code of `400` ("bad request"). A request for a missing entity will return the code `404` ("not found"). For a JSON endpoint, the body of an unsuccessful response will have an "error" key that describes the issue. For a CSV endpoint, you can expect an error message as a single line of text.

### Types of values

Decimal values will be encoded as strings, since JSON doesn't technically support floating-point values.

Timestamps are encoded as ISO 8601-formatted strings. All timestamps should be in UTC (timezone +00:00). In the structure descriptions below, they'll be indicated as `datetime`.

Public IDs of studies, experiments, and projects, are also strings, but have a specific structure, a zero-padded number prefixed by "SMGDB", "EMGDB", and "PMGDB", respectively

Technique units depend on what the specific technique is, but they will be one of:

- Cell count units: Cells/mL, Cells/μL
- CFU count units: CFUs/mL, CFUs/μL
- Metabolite units of molar or mass concentration: mM, μM, nM, pM, g/L, mg/L

Units within these three lists are convertible between each other in the application. To request data in specific units, append the corresponding query parameters to each query:

- `cellCountUnits`, example: `?cellCountUnits=Cells/μL`, default: `Cells/mL`
- `cfuCountUnits`, example: `?cfuCountUnits=CFUs/μL`, default: `CFUs/mL`
- `metaboliteUnits`, example: `?metaboliteUnits=g/L`, default: `mM`

For a combined example of all three, you can make a request to a particular endpoint with an added query string:

```
?cellCountUnits=Cells/μL&cfuCountUnits=CFUs/μL&metaboliteUnits=g/L`
```

There are also other units that are not convertible with the others:

- `AUC`: for metabolites, a relative measurement
- `g/L`: for mass concentration of cells, same unit as with metabolites, but non-convertible (since we don't know the weights of individual cells)
- `reads`: for relative cell abundances
- an empty string, indicating a unitless value like OD or pH.

Below, in the structure descriptions, these will be described as the type `Unit`. The original units that the data was uploaded in will be labeled "original", e.g. `techniqueOriginalUnits`.

### Permissions

The data in mGrowthDB is publicly available, but in some cases, it may not be published yet by its owners. In that case, these studies will not be available in the search and will only return limited data and metadata upon request.

Workspaces allow more fine-grained access. You can provide an API key to get read and write access to workspaces that you own. You can find this key in your profile page and reset it if it becomes compromised.

To pass the API key along to a request, you can attach it as the query parameter `apiKey`, or you can send it in a JSON payload. You can see examples of this in the "Workspaces" section. The API key can also be used to attach model predictions to measurement contexts that will be available for plotting on the web interface.

## Search

You can use the "search" endpoint to locate studies with specific properties. At this time, you can only look for studies that measure specific **microbial strains** or measure specific **metabolites**. Output structure:

```typescript
{
  studies: string[],
  experiments: string[],
  measurementTimeUnits: "h",
  measurementContexts: [{
    id: number,
    experimentId: "EMGDBxxx",
    studyId: "SMGDBxxx",
    techniqueType: "fc"|"od"|"plates"|"16s"|"qpcr"|"ph"|"metabolite",
    techniqueOriginalUnits: Unit,
    techniqueUnits: Unit,
    subject: {
      type: "bioreplicate"|"strain"|"metabolite",
      name: string,
      NCBId?: number,
      chebiId?: number,
    }
  }]
}
```

Example search query that looks for the strain with NCBI Taxonomy ID 411483, [Faecalibacterium duncaniae](https://www.ncbi.nlm.nih.gov/datasets/taxonomy/411483/):

```bash
curl -s "$ROOT_URL/api/v1/search.json?strainNcbiIds=411483"
```

Output:

```json
{
  "studies": [
    "SMGDB00000004",
    "SMGDB00000005"
  ],
  "experiments": [
    "EMGDB000000026",
    "EMGDB000000028",
    "EMGDB000000031",
    "EMGDB000000032",
    "EMGDB000000033",
    "EMGDB000000042",
    "EMGDB000000043"
  ],
  "measurementTimeUnits": "h",
  "measurementContexts": [
    {
      "id": 3478,
      "experimentId": "EMGDB000000028",
      "studyId": "SMGDB00000004",
      "techniqueType": "qpcr",
      "techniqueOriginalUnits": "Cells/mL",
      "techniqueUnits": "Cells/mL",
      "subject": {
        "type": "strain",
        "name": "Faecalibacterium prausnitzii A2-165",
        "NCBId": 411483
      }
    },
    ["...13 more entries..."],
    {
      "id": 5256,
      "experimentId": "EMGDB000000042",
      "studyId": "SMGDB00000005",
      "techniqueType": "fc",
      "techniqueOriginalUnits": "Cells/μL",
      "techniqueUnits": "Cells/mL",
      "subject": {
        "type": "strain",
        "name": "Faecalibacterium duncaniae",
        "NCBId": 411483
      }
    },
    ["...17 more entries..."]
  ]
}
```

The results include the public identifiers of studies and experiments that include measurements of that strain. You can dig into their details with the additional API calls described below.

The `measurementContexts` array includes the metadata of the measurement contexts that include the strain. You can iterate over the returned data and filter it additionally based on technique, measurement units, and so on.

Example 2: Searching by metabolite, in this case [N-acetylneuraminic acid](https://www.ebi.ac.uk/chebi/CHEBI:17012) with ChEBI ID 17012:

```bash
curl -s "$ROOT_URL/api/v1/search.json?metaboliteChebiIds=17012"
```

```json
{
  "studies": [
    "SMGDB00000002"
  ],
  "experiments": [
    "EMGDB000000021",
    "EMGDB000000023"
  ],
  "measurementTimeUnits": "h",
  "measurementContexts": [
    {
      "id": 3107,
      "experimentId": "EMGDB000000021",
      "studyId": "SMGDB00000002",
      "techniqueType": "metabolite",
      "techniqueOriginalUnits": "mM",
      "techniqueUnits": "mM",
      "subject": {
        "type": "metabolite",
        "name": "N-acetylneuraminic acid",
        "chebiId": 17012
      }
    },
    ["...7 more entries..."]
  ]
}
```

If you make a request for both strain and metabolite, the results will be the combination of both. In other words, the query will end up creating an `OR` operation. In practice, it might be best to make individual queries and process the results after downloading.

Note that the query terms are plural, `strainNcbiIds` and `metaboliteChebiIds`. You can make requests for multiple strains or metabolites by separating them with commas, for example:

```bash
curl -s "$ROOT_URL/api/v1/search.json?strainNcbiIds=411483,536231&metaboliteChebiIds=17234,17012"
```

Again, the result will be an OR operation, where records associated with any of the given search queries will be included. In this case, any measurements of [Faecalibacterium prausnitzii](https://www.ncbi.nlm.nih.gov/datasets/taxonomy/411483/), [Roseburia intestinalis L1-82](https://www.ncbi.nlm.nih.gov/datasets/taxonomy/536231/), [glucose](https://www.ebi.ac.uk/chebi/CHEBI:17234), or [trehalose](https://www.ebi.ac.uk/chebi/CHEBI:27082).

## Public entity metadata

There are three major entities with stable public ids: projects, studies, and experiments. We can fetch names, descriptions, and links to other entities from those central objects.

Workspaces are another entity we can read and write from that can be considered "stable" in terms of identifiers, but they can may be temporary depending on their owners choices. Interacting with workspaces will be discussed in a later section.

### Projects

Output structure:

```typescript
{
  id: "PMGDBxxx",
  name: string,
  description: string,
  studies: [{
    id: "SMGDBxxx",
    name: string,
  }]
}
```

Example project: [PMGDB000001](https://mgrowthdb.gbiomed.kuleuven.be/project/PMGDB000001).

```bash
curl -s "$ROOT_URL/api/v1/project/PMGDB000001.json"
```

Output:

```json
{
  "id": "PMGDB000001",
  "name": "Synthetic human gut bacterial community using an automated fermentation system",
  "description": "Six biological replicates for a community initially consisting of five common gut bacterial species that fill different metabolic niches. After an initial 12 hours in batch mode, we switched to chemostat mode and observed the community to stabilize after 2-3 days.",
  "studies": [
    {
      "id": "SMGDB00000001",
      "name": "Synthetic human gut bacterial community using an automated fermentation system"
    }
  ]
}
```

### Studies

Output structure:

```typescript
{
  id: "SMGDBxxx",
  projectId: "PMGDBxxx",
  name: string,
  description: string,
  url: string,
  uploadedAt: datetime,
  publishedAt: datetime,
  experiments: [{
    id: "EMGDBxxx",
    name: string,
  }]
}
```

Example study: [SMGDB00000002](https://mgrowthdb.gbiomed.kuleuven.be/study/SMGDB00000002/).

```bash
curl -s "$ROOT_URL/api/v1/study/SMGDB00000002.json"
```

Output:

```json
{
  "id": "SMGDB00000002",
  "name": "Starvation responses impact interaction of human gut bacteria BT-RI",
  "projectId": "PMGDB000002",
  "description": "we used an in vitro batch system containing mucin beads to emulate the dynamic host environment and to study its impact on the interactions between two abundant and prevalent human gut bacteria.",
  "url": "https://doi.org/10.1038/s41396-023-01501-1",
  "uploadedAt": "2025-06-05T16:52:49+00:00",
  "publishedAt": "2025-06-05T16:52:53+00:00",
  "experiments": [
    {
      "id": "EMGDB000000019",
      "name": "BT_MUCIN"
    },
    {
      "id": "EMGDB000000020",
      "name": "BT_WC"
    },
    ["...4 more entries..."]
  ]
}
```

### Experiments

Output structure (note that compartment values encoded as decimal numbers are returned as strings):

```typescript
{
  id: "EMGDBxxx",
  name: string,
  description: string,
  studyId: "SMGDBxxx",
  cultivationMode: "batch"|"fed-batch"|"chemostat"|"other",
  communityStrains: [{
    id: number,
    NCBId: number,
    custom: boolean,
    name: string,
  }],
  compartments: [{
    name: string,
    volume?: string,
    pressure?: string,
    stirringSpeed?: string,
    stirringMode?: "linear"|"orbital"|"vibrational",
    O2?: string,
    CO2: string,
    H2?: string,
    N2?: string,
    inoculumConcentration?: string,
    inoculumVolume?: string,
    initialPh?: string,
    dilutionRate?: string,
    initialTemperature?: string,
    mediumName?: string,
    mediumUrl?: string,
  }],
  bioreplicates: [{
    id: number,
    name: string
    biosampleUrl?: string,
    isAverage: boolean,
    measurementContexts: [{
      id: number,
      experimentId: "EMGDBxxx",
      studyId: "SMGDBxxx",
      techniqueType: "fc"|"od"|"plates"|"16s"|"qpcr"|"ph"|"metabolite",
      techniqueOriginalUnits: Unit,
      techniqueUnits: Unit,
      subject: {
        type: "bioreplicate"|"strain"|"metabolite",
        name: string,
        NCBId?: number,
        chebiId?: number,
      }
    }]
  }]
}
```

Example experiment: [EMGDB000000019](https://mgrowthdb.gbiomed.kuleuven.be/experiment/EMGDB000000019/)

```bash
curl -s "$ROOT_URL/api/v1/experiment/EMGDB000000019.json"
```

Example output:

```json
{
  "id": "EMGDB000000019",
  "name": "BT_MUCIN",
  "description": "BT with WC plus mucin beads for 120 h",
  "studyId": "SMGDB00000002",
  "cultivationMode": "batch",
  "communityStrains": [
    {
      "id": 60031,
      "NCBId": 818,
      "custom": false,
      "name": "Bacteroides thetaiotaomicron"
    }
  ],
  "compartments": [
    {
      "name": "WC",
      "volume": "60.00",
      "pressure": "1.00",
      "stirringSpeed": 170.0,
      "stirringMode": "linear",
      "O2": null,
      "CO2": "10.00",
      "H2": "10.00",
      "N2": "80.00",
      "inoculumConcentration": "1960000.000",
      "inoculumVolume": "1.00",
      "initialPh": "6.70",
      "dilutionRate": null,
      "initialTemperature": "37.00",
      "mediumName": "Wilkins-Chalgren Anaerobe Broth (WC)",
      "mediumUrl": "https://mediadive.dsmz.de/medium/339"
    },
    {
      "name": "MUCIN",
      "volume": null,
      "pressure": null,
      "stirringSpeed": null,
      "stirringMode": "",
      "O2": null,
      "CO2": null,
      "H2": null,
      "N2": null,
      "inoculumConcentration": null,
      "inoculumVolume": null,
      "initialPh": null,
      "dilutionRate": null,
      "initialTemperature": "37.00",
      "mediumName": "Mucin",
      "mediumUrl": null,
    }
  ],
  "bioreplicates": [
    {
      "id": 60111,
      "name": "Average(BT_MUCIN)",
      "biosampleUrl": null,
      "isAverage": true,
      "measurementContexts": [
        {
          "id": 1431,
          "techniqueType": "od",
          "techniqueOriginalUnits": "",
          "techniqueUnits": "",
          "subject": {
            "id": 60111,
            "type": "bioreplicate",
            "name": "Average(BT_MUCIN)"
          }
        },
        {
          "id": 1432,
          "techniqueType": "ph",
          "techniqueOriginalUnits": "",
          "techniqueUnits": "",
          "subject": {
            "id": 60111,
            "type": "bioreplicate",
            "name": "Average(BT_MUCIN)"
          }
        },
        "[...5 more entries...]"
      ]
    },
    "[...3 more entries...]"
  ]
}
```

## Measurement data

### For a single measurement context

From one of the above measurement context records, we can find the id of a particular collection of measurements and fetch its metadata as JSON and its specific measurements in CSV format.

Metadata structure:

```typescript
{
  id: number,
  experimentId: "EMGDBxxx",
  studyId: "SMGDBxxx",
  bioreplicateId: number,
  bioreplicateName: string,
  techniqueType: "fc"|"od"|"plates"|"16s"|"qpcr"|"ph"|"metabolite",
  techniqueOriginalUnits: Unit,
  techniqueUnits: Unit,
  subject: {
    type: "bioreplicate"|"strain"|"metabolite",
    name: string,
    NCBId?: number,
    chebiId?: number,
  },
  measurementCount: number,
  measurementTimeUnits: "h",
}
```

To fetch the metadata via curl:

```bash
curl -s "$ROOT_URL/api/v1/measurement-context/1440.json"
```

Example output:

```json
{
  "id": 1440,
  "experimentId": "EMGDB000000020",
  "studyId": "SMGDB00000002",
  "bioreplicateId": 60329,
  "bioreplicateName": "Average(BT_WC)",
  "techniqueType": "fc",
  "techniqueOriginalUnits": "Cells/μL",
  "techniqueUnits": "Cells/mL",
  "measurementCount": 14,
  "measurementTimeUnits": "h"
  "modelPredictionIds": [],
  "subject": {
    "type": "strain",
    "name": "Bacteroides thetaiotaomicron VPI-5482",
    "NCBId": 226186
  },
}
```

This gives us information about the specifics of the measurement context like what its technique is, what units the value is measured in, and the public ids of its containing experiment and study. To fetch the full dataset for this measurement context with "time" measured in hours:

```bash
curl -s "$ROOT_URL/api/v1/measurement-context/1440.csv"
```

Example output:

```
time,value,std
0.0,2619.0,477.072
4.0,36072.333,1522.018
12.0,1003028.333,30201.503
16.0,1106725.0,85176.706
24.0,857815.0,62848.275
28.0,778893.333,47670.388
32.0,962915.0,55489.511
38.0,675345.0,26650.222
48.0,348478.333,102905.344
60.0,111021.667,28523.155
72.0,45606.667,13966.714
96.0,13413.333,4155.786
120.0,3215.0,461.808
```

If the measurement context does not have standard deviation values, the "std" column will be present, but empty. Example measurement and its data:

```bash
curl -s "$ROOT_URL/api/v1/measurement-context/1314.json"
curl -s "$ROOT_URL/api/v1/measurement-context/1314.csv"
```

```json
{
  "id": 1314,
  "experimentId": "EMGDB000000020",
  "studyId": "SMGDB00000002",
  "bioreplicateId": 60315,
  "bioreplicateName": "BT_WC_3",
  "techniqueType": "metabolite",
  "techniqueOriginalUnits": "mM",
  "techniqueUnits": "mM",
  "measurementCount": 14,
  "measurementTimeUnits": "h"
  "modelPredictionIds": [],
  "subject": {
    "type": "metabolite",
    "name": "succinate",
    "chebiId": 26806
  },
}
```

```
time,value,std
0.0,0.57,
4.0,0.53,
8.0,2.19,
12.0,5.04,
16.0,7.67,
24.0,9.58,
28.0,10.66,
32.0,10.67,
38.0,10.69,
48.0,10.99,
60.0,11.06,
72.0,10.94,
96.0,11.0,
120.0,11.03,
```

### For an entire biological replicate

We can perform similar queries for biological replicates, getting the results for multiple measurement contexts in one CSV, grouped by measurement context id. We can get the bioreplicate IDs from the experiment metadata and use them to fetch either the bioreplicate-specific metadata or the measurements in CSV form.

Output structure:

```typescript
{
  id: number,
  experimentId: "EMGDBxxx",
  studyId: "SMGDBxxx",
  name: string,
  biosampleUrl: null,
  isAverage: boolean,
  measurementTimeUnits: "h",
  measurementContexts: [{
    id: number,
    techniqueType: "fc"|"od"|"plates"|"16s"|"qpcr"|"ph"|"metabolite",
    techniqueOriginalUnits: Unit,
    techniqueUnits: Unit,
    subject: {
      type: "bioreplicate"|"strain"|"metabolite",
      name: string,
      NCBId?: number,
      chebiId?: number,
    }
  }]
}
```

The CSV for a biological replicate includes additional context about the subject of each measurement: its type and name, and external database identifier, if applicable. This information can be seen in the JSON metadata, but it's included in the CSV for convenience.

```bash
curl -s "$ROOT_URL/api/v1/bioreplicate/1314.json"
curl -s "$ROOT_URL/api/v1/bioreplicate/1314.csv"
```

```json
{
  "id": 60332,
  "experimentId": "EMGDB000000023",
  "studyId": "SMGDB00000002",
  "name": "Average(BTRI_MUCIN)",
  "biosampleUrl": null,
  "isAverage": true,
  "measurementTimeUnits": "h",
  "measurementContexts": [
    {
      "id": 3364,
      "techniqueType": "od",
      "techniqueOriginalUnits": "",
      "techniqueUnits": "",
      "subject": {
        "type": "bioreplicate",
        "name": "Average(BTRI_MUCIN)"
      }
    },
    ["...17 more entries..."]
  ]
}
```

```
measurementContextId,subjectType,subjectName,subjectExternalId,time,value,std
3328,bioreplicate,Average(BT_WC),,0.0,0.006,0.001
3328,bioreplicate,Average(BT_WC),,4.0,0.034,0.0
3328,bioreplicate,Average(BT_WC),,8.0,0.406,0.001
3328,bioreplicate,Average(BT_WC),,12.0,0.796,0.002
3328,bioreplicate,Average(BT_WC),,16.0,0.965,0.001
3328,bioreplicate,Average(BT_WC),,24.0,0.705,0.002
3328,bioreplicate,Average(BT_WC),,28.0,0.659,0.003
3328,bioreplicate,Average(BT_WC),,32.0,0.657,0.0
3328,bioreplicate,Average(BT_WC),,38.0,0.868,0.006
3328,bioreplicate,Average(BT_WC),,48.0,0.909,0.003
3328,bioreplicate,Average(BT_WC),,60.0,0.921,0.004
3328,bioreplicate,Average(BT_WC),,72.0,0.92,0.002
3328,bioreplicate,Average(BT_WC),,96.0,0.909,0.002
3328,bioreplicate,Average(BT_WC),,120.0,0.905,0.001
3329,bioreplicate,Average(BT_WC),,0.0,6.613,0.019
3329,bioreplicate,Average(BT_WC),,4.0,6.623,0.019
3329,bioreplicate,Average(BT_WC),,8.0,6.15,0.0
3329,bioreplicate,Average(BT_WC),,12.0,5.42,0.0
3329,bioreplicate,Average(BT_WC),,16.0,5.073,0.024
3329,bioreplicate,Average(BT_WC),,24.0,5.027,0.019
3329,bioreplicate,Average(BT_WC),,28.0,4.97,0.0
3329,bioreplicate,Average(BT_WC),,32.0,4.983,0.019
3329,bioreplicate,Average(BT_WC),,38.0,5.023,0.019
3329,bioreplicate,Average(BT_WC),,48.0,5.14,0.0
3329,bioreplicate,Average(BT_WC),,60.0,5.09,0.0
3329,bioreplicate,Average(BT_WC),,72.0,5.09,0.0
3329,bioreplicate,Average(BT_WC),,96.0,5.14,0.0
3329,bioreplicate,Average(BT_WC),,120.0,5.113,0.024
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,0.0,2619.0,477.072
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,4.0,36072.333,1522.018
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,12.0,1003028.333,30201.503
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,16.0,1106725.0,85176.706
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,24.0,857815.0,62848.275
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,28.0,778893.333,47670.388
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,32.0,962915.0,55489.511
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,38.0,675345.0,26650.222
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,48.0,348478.333,102905.344
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,60.0,111021.667,28523.155
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,72.0,45606.667,13966.714
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,96.0,13413.333,4155.786
3330,strain,Bacteroides thetaiotaomicron VPI-5482,NCBI:226186,120.0,3215.0,461.808
3331,metabolite,pyruvate,CHEBI:15361,0.0,9.663,0.061
3331,metabolite,pyruvate,CHEBI:15361,4.0,9.69,0.127
[...218 more lines...]
```

## Model predictions

The database includes modeling functionality -- users can fit models in the application interface, or they can upload custom models. The modeling records will be returned when fetching measurement contexts in the `modelPredictionIds` key, which in the examples so far has been empty.

### Fetching data

If you have a model prediction id, you can fetch the JSON metadata that describes this fit and a CSV of its predictions from the `/model-prediction/` endpoint.

Structure:

```typescript
{
  id: number,
  measurementContextId: number,
  studyId: "SMGDBxxx",
  type: "easy_linear"|"logistic"|"baranyi_roberts"|"custom_<number>",
  params: dict,
  calculatedAt: datetime,
}
```

The `params` dictionary will have variable contents that describe input parameters to the modeling process, quality of fit, growth parameters, and potentially other important information. If the type of the model is a custom one, the `type` key will start with `custom_` but have a variable label.

Example:

```bash
curl -s "$ROOT_URL/api/v1/model-prediction/29.json"
curl -s "$ROOT_URL/api/v1/model-prediction/29.csv"
```

```json
{
  "id": 29,
  "measurementContextId": 9522,
  "studyId": "SMGDB00000007",
  "type": "logistic",
  "params": {
    "fit": {
      "r2": "0.9972",
      "rss": "0.0942"
    },
    "inputs": {
      "endTime": "30"
    },
    "r_version": "4.4.3 (2025-02-28)",
    "coefficients": {
      "K": "858879.5694",
      "y0": "2381.8389",
      "mumax": "0.6582"
    },
    "growthrates_version": "0.8.5"
  },
  "calculatedAt": "Tue, 20 Jan 2026 10:53:39 GMT"
}
```

```
time,value,std
0.0,2381.8389,
0.6030150753768844,3537.524301675712,
1.2060301507537687,5250.519088490064,
1.809045226130653,7785.456559068567,
[...196 more lines...]
```

### Pushing data

If you provide an API key, you can attach custom model predictions to individual measurement contexts from the API. This is similar to how you would use workspaces, described in the next section. Here is an example payload that can be sent to one of these endpoints:

```json
{
  "apiKey": "[redacted]",
  "units": "Cells/μL",
  "data": "time,value,std\n0.0,2197.0,\n4.0,2105.0,\n8.0,2505.0,\n",
  "model": {
      "name": "My custom model",
      "shortName": "MCM",
      "url": "my-custom-model.example.com",
      "description": "A custom model."
  }
}
```

Most of the model information is optional, only the "name" key is mandatory. To learn more about uploading data and defining a custom model, read the "Uploading custom model data" section in the "[Modeling interface](https://mgrowthdb.gbiomed.kuleuven.be/help/modeling-interface/)" section of the help files.

We can save this file as `payload.json` and then trigger a curl request, passing it along like this:

```bash
curl -s "$ROOT_URL/api/v1/measurement-context/123/model-predictions.json" \
    --header "Content-Type: application/json" \
    --data @payload.json
```

The measurement context ID given in the example is arbitrary. Ideally, it's recommended to fetch data through the "experiment" endpoint, associate the data you're operating on with its measurement context ID, and then push predictions to the `model-predictions.json` endpoint. The response at this time only contains a `{'status': 'ok'}` payload if successful. In case of a validation error or missing required data, you should receive the appropriate HTTP status code and JSON describing the issue.

## Workspaces

A workspace is identified by two parameters:

- The [ORCID](https://orcid.org/) of the user that owns the workspace
- The name of the workspace, which defaults to "default".

A user can delete or create new workspaces, but their default workspace will always exist, as long as they have an account in the application. Data from workspaces can be read, but you can also push data to workspaces, as long as you provide the API key found on your profile page.

You can only push data to your own workspaces and it will appear in the "API" section.

You can only read a workspace's data and metadata if the workspace is made publicly available, or if the API key you're using identifies you as the owner of the workspace. See the "Permissions" section above for details and continue reading to see example usage below.

### Reading workspace data

To get metadata about a particular workspace, you can make a request to the `/workspace/` endpoint with the parameters described above. The response structure should look like the following:

```typescript
{
  name: string,
  entries: [{
    id: number,
    label: string,
    units?: Unit,
    sourceType?: "upload" | "api",
    dataType?: "measurement" | "model" | "other",
    subjectType?: "community" | "strain" | "metabolite",
  }]
}
```

Note that most of the metadata is nullable. A user can upload data without providing any details about its nature.

Example request:

```bash
curl -s "$ROOT_URL/api/v1/workspace/0009-0004-1479-7441/default.json"
```

This will fetch the "default" workspace for the user with ORCID `0009-0004-1479-7441`. An example output:

```json
{
  "name": "default",
  "entries": [
    {
      "id": 257,
      "label": "FC live of the bh1_A community",
      "units": "Cells/μL",
      "sourceType": "upload",
      "dataType": "measurement",
      "subjectType": "community"
    },
    {
      "id": 258,
      "label": "FC of Bacteroides thetaiotaomicron VPI-5482 in Average(bhbtri)",
      "units": "Cells/μL",
      "sourceType": "upload",
      "dataType": "measurement",
      "subjectType": "strain"
    },
    {
      "id": 259,
      "label": "Baranyi-Roberts predictions",
      "units": "Cells/μL",
      "sourceType": "upload",
      "dataType": "model",
      "subjectType": "strain"
    }
  ]
}
```

An individual workspace entry's metadata can also be fetched by id. For instance:

```bash
curl -s "$ROOT_URL/api/v1/workspace-entry/257.json"
```

The output is the same metadata seen above:

```json
{
  "id": 257,
  "label": "FC live of the bh1_A community",
  "units": "Cells/μL",
  "sourceType": "upload",
  "dataType": "measurement",
  "subjectType": "community"
}
```

We can also get the uploaded data by fetching the CSV endpoint:

```bash
curl -s "$ROOT_URL/api/v1/workspace-entry/257.csv"
```

Output:

```
time,value,error
0.0,2197000.0,
4.0,2105000.0,
8.0,2505000.0,
12.0,10255000.0,
16.0,24660000.0,
20.0,94715000.0,
24.0,318410000.0,
28.0,671785000.0,
32.0,960330000.0,
36.0,859940000.0,
40.0,1113985000.0,
44.0,981155000.0,
48.0,847580000.0,
60.0,233545000.0,
72.0,123860000.0,
96.0,110720000.0,
120.0,74315000.0,
```

### Pushing data with an API key

You can send a POST request to one of your workspaces with a package of data entries that will be processed into "workspace entry" records. The endpoint only includes the workspace name and not the user's ORCID: `/workspace/<name>.json`. That's because it also takes a mandatory API key that uniquely identifies a user. Here is an example payload that can be sent to a workspace endpoint:

```json
{
  "apiKey": "[redacted]",
  "entries": [{
    "label": "API push test",
    "data": "time,value,std\n0.0,2197.0,\n4.0,2105.0,\n8.0,2505.0,\n",
    "dataType": "measurement",
    "subjectType": "strain",
    "units": "Cells/μL"
  }]
}
```

Note that the "apiKey" field is redacted -- it will only work if you place your own API key there. The raw data is encoded as a CSV string. The first column will always be interpreted as the time values, the second, whatever its name, will be considered to contain measurement values, while the third, if present, will be the error column.

You can provide as many entries as you like, and they will be created in the order they appear in the JSON payload. That way, you can group them together logically, e.g. pushing observational measurements and their model in sequential pairs. Most of the metadata is also optional. If the "label" is missing, it will be taken from the column name of the second column of the data.

We can save this file as `payload.json` and then trigger a curl request, passing it along like this:

```bash
curl -s "$ROOT_URL/api/v1/workspaces/default.json" \
    --header "Content-Type: application/json" \
    --data @payload.json
```

The returned result includes the URL of the workspace where you can find the data, a "visualize" URL that will show the visualize page of that workspace with the "API" data source selected, and a list of the workspace entry IDs that were created by your action:

```json
{
  "workspaceUrl": "https://mgrowthdb.gbiomed.kuleuven.be/workspaces/0009-0004-1479-7441/default/",
  "workspaceVisualizeUrl": "https://mgrowthdb.gbiomed.kuleuven.be/workspaces/0009-0004-1479-7441/default/visualize/?selectedSourceType=api",
  "workspaceEntryIds": [
    260
  ]
}
```

It's important to note that, if you trigger this request again, the previous API-created records in that workspace will be deleted and the given entries will be created. Each push **replaces** the data in that workspace, though only the entries that were previously pushed via the API (with a `sourceType` field of `api`). Files uploaded directly through the web interface will not be affected. This is done so that re-running scripts that push to the workspace do not end up accidentally accumulating many duplicate records.

If you'd like to avoid deleting your previous entries, you need to provide an `append` query parameter, for example:

```bash
curl -s "$ROOT_URL/api/v1/workspaces/default.json?append=1" \
    --header "Content-Type: application/json" \
    --data @payload.json
```

Running this curl request will end up duplicating the data in the "API" section, but if you have multiple different payloads, you might be looking to push them one at a time.
