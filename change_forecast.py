
import streamlit as st
import pandas as pd
import data

from datetime import datetime
from io import BytesIO


YEAR_OPTIONS = list(range(2020, 2027))

MONTHS_OPTIONS = {
    "January": 1, "February": 2, "March": 3,
    "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9,
    "October": 10, "November": 11, "December": 12
}

DEPARTMENT_OPTIONS = ["IT", "QD", "SCM"]

UPLOAD_COLUMNS = ["Department", "Period", "Budget"]


def create_excel_template():

    template_df = pd.DataFrame(columns=UPLOAD_COLUMNS)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        template_df.to_excel(
            writer,
            index=False,
            sheet_name="Budget Upload"
        )

    return output.getvalue()


def validate_upload(uploaded_file):

    df_upload = pd.read_excel(uploaded_file)

    errors = []

    # Validate columns
    missing_columns = [
        col for col in UPLOAD_COLUMNS
        if col not in df_upload.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing columns: {', '.join(missing_columns)}"
        )
        return None, errors

    df_upload = df_upload[UPLOAD_COLUMNS].copy()

    if df_upload.empty:
        errors.append("The uploaded file contains no records.")
        return None, errors

    # Validate department
    df_upload["Department"] = (
        df_upload["Department"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    invalid_departments = (
        ~df_upload["Department"].isin(DEPARTMENT_OPTIONS)
    )

    if invalid_departments.any():
        invalid_values = (
            df_upload.loc[invalid_departments, "Department"]
            .dropna()
            .unique()
            .tolist()
        )

        errors.append(
            f"Invalid departments: {invalid_values}"
        )

    # Validate period
    df_upload["Period"] = pd.to_datetime(
        df_upload["Period"],
        errors="coerce"
    )

    invalid_dates = df_upload["Period"].isna()

    if invalid_dates.any():
        errors.append(
            f"Invalid dates in rows: "
            f"{(df_upload.index[invalid_dates] + 2).tolist()}"
        )

    # Normalize periods to the first day of the month
    df_upload["Period"] = (
        df_upload["Period"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Validate budget
    df_upload["Budget"] = pd.to_numeric(
        df_upload["Budget"],
        errors="coerce"
    )

    invalid_budgets = (
        df_upload["Budget"].isna()
        | (df_upload["Budget"] < 0)
    )

    if invalid_budgets.any():
        errors.append(
            f"Invalid budgets in rows: "
            f"{(df_upload.index[invalid_budgets] + 2).tolist()}"
        )

    # Check duplicate department-period combinations
    duplicates = df_upload.duplicated(
        subset=["Department", "Period"],
        keep=False
    )

    if duplicates.any():
        duplicate_records = df_upload.loc[
            duplicates, ["Department", "Period"]
        ]

        errors.append(
            "Duplicate department-period combinations found: "
            f"{duplicate_records.to_dict('records')}"
        )

    if errors:
        return None, errors

    return df_upload, errors


def run_change_forecast_page():

    st.set_page_config(
        layout="wide",
        page_title="Manual Budget Update"
    )

    st.title("Manual Budget Update")
    st.caption("Manage monthly departmental budgets.")

    # Initialize session state
    if "department_selected" not in st.session_state:
        st.session_state["department_selected"] = "IT"

    # Department selection
    department = st.selectbox(
        "Select department",
        options=DEPARTMENT_OPTIONS,
        key="department_selected"
    )

    # Application tabs
    manual_tab, bulk_tab = st.tabs([
        "Manual Update",
        "Bulk Upload"
    ])

    # --------------------------------
    # MANUAL UPDATE
    # --------------------------------

    with manual_tab:

        st.subheader("Budget entry")

        with st.container(border=True):

            with st.form("budget_update_form"):

                col1, col2, col3 = st.columns(3)

                with col1:
                    year = st.selectbox(
                        "Year",
                        options=YEAR_OPTIONS
                    )

                with col2:
                    month = st.selectbox(
                        "Month",
                        options=list(MONTHS_OPTIONS.keys())
                    )

                with col3:
                    budget = st.number_input(
                        "Budget",
                        min_value=0.0,
                        step=1000.0,
                        format="%.2f"
                    )

                submitted = st.form_submit_button(
                    "Save budget",
                    type="primary",
                    use_container_width=True
                )

                if submitted:

                    period = datetime(
                        year=year,
                        month=MONTHS_OPTIONS[month],
                        day=1
                    )

                    record = (department, period, budget)

                    try:
                        data.add_value(record)

                        st.success(
                            f"Budget saved: {department} | "
                            f"{month} {year}"
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(f"Could not save budget: {e}")

    # --------------------------------
    # BULK UPLOAD
    # --------------------------------

    with bulk_tab:

        st.subheader("Upload multiple budget records")

        st.write(
            "Download the Excel template, populate it with "
            "your budget records and upload the completed file."
        )

        # Download template
        st.download_button(
            label="Download Excel template",
            data=create_excel_template(),
            file_name="budget_upload_template.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

        st.divider()

        uploaded_file = st.file_uploader(
            "Upload budget file",
            type=["xlsx"]
        )

        if uploaded_file is not None:

            try:
                df_upload, errors = validate_upload(uploaded_file)

                if errors:

                    st.error("The uploaded file contains errors:")

                    for error in errors:
                        st.write(f"- {error}")

                else:

                    st.success(
                        f"Validation successful. "
                        f"{len(df_upload)} records ready for upload."
                    )

                    st.subheader("Preview uploaded records")

                    st.dataframe(
                        df_upload,
                        hide_index=True,
                        use_container_width=True
                    )

                    confirm_upload = st.button(
                        "Confirm and upload",
                        type="primary",
                        use_container_width=True
                    )

                    if confirm_upload:

                        records = [
                            (
                                row.Department,
                                row.Period.to_pydatetime(),
                                float(row.Budget)
                            )
                            for row in df_upload.itertuples(
                                index=False
                            )
                        ]

                        try:
                            data.add_values(records)

                            st.success(
                                f"Successfully processed "
                                f"{len(records)} budget records."
                            )

                            st.rerun()

                        except Exception as e:
                            st.error(
                                f"Upload failed: {e}"
                            )

            except Exception as e:
                st.error(
                    f"Could not read uploaded file: {e}"
                )

    # --------------------------------
    # CURRENT BUDGET RECORDS
    # --------------------------------

    st.divider()

    st.subheader(
        f"Current budget records – {department}"
    )

    df = data.select_costs_by_dept()

    df_filtered = df[
        df["Department Name"] == department
    ]

    st.dataframe(
        df_filtered,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Department Name": "Department",
            "Period": st.column_config.DateColumn(
                "Period",
                format="YYYY-MM-DD"
            ),
            "Cost Value": st.column_config.NumberColumn(
                "Budget",
                format="%,.2f"
            )
        }
    )
