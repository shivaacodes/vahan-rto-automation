# Vahan RTO Automation

This project automates the downloading of daily Excel reports for all 87 Kerala RTOs from the Vahan Parivahan dashboard.

## Setup

1. **Prerequisites**: Python 3.8+
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## Configuration

All configuration is centralized in `config.py`. Here you can update:
- **Filters**: State, Y-Axis, X-Axis, Year Type, and Year.
- **Selectors**: If the Vahan dashboard is updated, you may need to update the DOM selectors here. 
  - *Tip for fixing selectors*: Use your browser's Developer Tools (F12). Note that Vahan uses PrimeFaces `selectOneMenu` for dropdowns, meaning the actual `<select>` tag is hidden and replaced with a `<ul>`/`<li>` structure dynamically.
- **Timeouts**: Adjust the polling/wait times if the portal is slower than usual.

## Running the Automation

To run the script:
```bash
python download_reports.py
```

### Features:
- **Idempotency**: Re-running on the same day will seamlessly overwrite existing files without creating duplicates.
- **Resiliency**: If a specific RTO fails to download (e.g. due to a network timeout), the script will continue with the rest and retry the failed ones at the end.
- **Logging**: Detailed logs for each run are saved in the `logs/` directory.
- **Polite Rate Limiting**: The script pauses for 2 seconds between each iteration to prevent hammering the server.

## Output

- **Reports**: Saved in `reports/YYYY-MM-DD/` with names formatted as `<RTO_CODE>.xlsx` (e.g. `KL7.xlsx`). Note that the raw downloaded files from the dashboard are HTML tables disguised with `.xls`, but they are saved as `.xlsx` as requested and can be opened in Excel (Excel may display a format warning prompt upon opening, which is normal for Vahan reports).
- **Logs**: Saved in `logs/` with names formatted as `run_YYYY-MM-DD.log`.
