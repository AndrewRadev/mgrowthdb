# Release notes

## v1.1.0

- Scripts to sync data with NCBI (JensenLab) and ChEBI:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/55>.

- Docker setup for development purposes, e.g. for people who want to run and try the app on windows:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/58>

- API for muGrowthCtrl to access:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/69>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/73>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/93>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/94>

- Upload process improvements:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/57>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/78>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/91>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/95>

- Internal refactoring: Extract "study techniques" as parents to "measurement techniques". This enables us to add labels to techniques and separate live/dead/total cell measurements
    * <https://github.com/AndrewRadev/mgrowthdb/pull/79>

- New search interface:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/79>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/86>

- Custom model uploads:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/84>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/85>

- Sandbox page:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/87>

- Page visit counting. This should give us an idea of the relative popularity of the project.
    * <https://github.com/AndrewRadev/mgrowthdb/pull/88>

- Publication authorship. Pretty important to have clear authorship of the studies that are not ours.
    * <https://github.com/AndrewRadev/mgrowthdb/pull/90>

- A lot of smaller improvements:
    * <https://github.com/AndrewRadev/mgrowthdb/pull/60>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/63>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/72>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/75>
    * <https://github.com/AndrewRadev/mgrowthdb/pull/80>

## v1.0.0

<https://github.com/msysbio/bacterial_growth/releases/tag/v1.0.0>

Rebuild of the microbial growth database. Migrated from a streamlit app to a flask-based website, made lots of backend and UI changes.
