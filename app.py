import streamlit as st
import pandas as pd
import io
from datetime import datetime
import plotly.express as px
import os

# Page configuration
st.set_page_config(
    page_title="CSV Cleaner Pro",
    page_icon="🧹",
    layout="wide"
)

# Initialize session state for download tracking
if 'download_count' not in st.session_state:
    st.session_state.download_count = 0
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

# App title and description
st.title("🧹 CSV & Excel Cleaner Pro")
st.markdown("""
Upload your messy CSV or Excel file and let our AI-powered cleaner:
- ✅ Remove empty rows and columns
- ✅ Standardize column names (lowercase, no spaces)
- ✅ Fix date formats
- ✅ Remove duplicates
- ✅ Handle missing values intelligently
""")

# Sidebar for options and pricing
with st.sidebar:
    st.header("⚙️ Cleaning Options")
    
    remove_empty_rows = st.checkbox("Remove empty rows", value=True)
    remove_empty_cols = st.checkbox("Remove empty columns", value=True)
    standardize_names = st.checkbox("Standardize column names", value=True)
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    fill_missing = st.checkbox("Fill missing values", value=True)
    
    st.divider()
    
    st.header("💰 Pricing")
    
    # Show download counter
    remaining_downloads = max(0, 2 - st.session_state.download_count)
    
    if remaining_downloads > 0:
        st.success(f"✨ **{remaining_downloads} FREE downloads remaining**")
        st.info("Then just **$9/month** for unlimited access")
    else:
        st.warning("⚠️ **Free downloads exhausted**")
        st.info("Subscribe for **$9/month** for unlimited access")
    
    # Gumroad payment button (replace with your actual Gumroad link)
    gumroad_link = "https://your-gumroad-link.com"  # Replace this!
    
    st.markdown(f"""
    <a href="{gumroad_link}" target="_blank">
        <button style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
            transition: transform 0.2s;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);">
            💳 Subscribe Now - $9/month
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("✓ Cancel anytime")
    st.caption("✓ Instant access after payment")
    st.caption("✓ Email support included")
    
    # Reset button for testing
    st.divider()
    if st.button("🔄 Reset Download Counter (Testing)"):
        st.session_state.download_count = 0
        st.rerun()

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Upload Your File")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Maximum file size: 200MB"
    )

# Process the file if uploaded
if uploaded_file is not None:
    try:
        # Read the file
        with st.spinner('Processing your file...'):
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Store original for comparison
            original_df = df.copy()
            original_shape = df.shape
            
            with col1:
                st.subheader("📊 Original Data")
                st.write(f"Shape: {original_shape[0]} rows × {original_shape[1]} columns")
                
                # Show data quality issues
                issues = []
                missing_count = df.isnull().sum().sum()
                duplicate_count = df.duplicated().sum()
                
                if missing_count > 0:
                    issues.append(f"• {missing_count} missing values")
                if duplicate_count > 0:
                    issues.append(f"• {duplicate_count} duplicate rows")
                if any(df.columns.str.contains(' ', na=False)):
                    issues.append("• Column names contain spaces")
                if any(df.columns.str.contains('[A-Z]', na=False)):
                    issues.append("• Column names have inconsistent casing")
                
                # Display issues
                if issues:
                    st.subheader("🔍 Issues Found")
                    for issue in issues:
                        st.warning(issue)
                else:
                    st.success("✅ No major issues detected!")
                
                # Show sample
                st.dataframe(df.head(10), use_container_width=True)
            
            # APPLY CLEANING
            cleaned_df = df.copy()
            
            if remove_empty_rows:
                cleaned_df = cleaned_df.dropna(how='all')
            
            if remove_empty_cols:
                cleaned_df = cleaned_df.dropna(axis=1, how='all')
            
            if standardize_names:
                cleaned_df.columns = [
                    str(col).strip().lower().replace(' ', '_').replace('-', '_') 
                    for col in cleaned_df.columns
                ]
            
            if remove_duplicates:
                cleaned_df = cleaned_df.drop_duplicates()
            
            if fill_missing:
                # Fill missing values intelligently
                for col in cleaned_df.columns:
                    if cleaned_df[col].dtype == 'object':
                        cleaned_df[col] = cleaned_df[col].fillna('')
                    else:
                        # For numeric columns, fill with median
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median() if not cleaned_df[col].isnull().all() else 0)
            
            with col2:
                st.subheader("✨ Cleaned Data")
                st.write(f"Shape: {cleaned_df.shape[0]} rows × {cleaned_df.shape[1]} columns")
                
                # Show improvements
                rows_removed = original_shape[0] - cleaned_df.shape[0]
                cols_removed = original_shape[1] - cleaned_df.shape[1]
                
                # Metrics in columns
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric("Rows removed", rows_removed, delta_color="inverse")
                with metric_col2:
                    st.metric("Columns removed", cols_removed, delta_color="inverse")
                with metric_col3:
                    st.metric("Issues fixed", len(issues))
                
                # Show cleaned sample
                st.dataframe(cleaned_df.head(10), use_container_width=True)
                
                # Download section
                st.subheader("💾 Download Cleaned File")
                
                # Check if user can download
                if st.session_state.download_count < 2:
                    # Convert to CSV
                    csv = cleaned_df.to_csv(index=False)
                    
                    # Create Excel buffer for Excel download
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        cleaned_df.to_excel(writer, index=False, sheet_name='Cleaned Data')
                    
                    # Download buttons
                    dl_col1, dl_col2 = st.columns(2)
                    
                    with dl_col1:
                        if st.button("📥 Download as CSV", key="csv_btn"):
                            st.session_state.download_count += 1
                            st.download_button(
                                label="Click to Save CSV",
                                data=csv,
                                file_name=f"cleaned_{uploaded_file.name.replace('.xlsx', '.csv').replace('.xls', '.csv')}",
                                mime="text/csv",
                                key="csv_download"
                            )
                    
                    with dl_col2:
                        if st.button("📥 Download as Excel", key="excel_btn"):
                            st.session_state.download_count += 1
                            st.download_button(
                                label="Click to Save Excel",
                                data=excel_buffer.getvalue(),
                                file_name=f"cleaned_{uploaded_file.name}",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="excel_download"
                            )
                    
                    # Show remaining downloads
                    remaining = 2 - st.session_state.download_count
                    st.info(f"📥 {remaining} free {'download' if remaining == 1 else 'downloads'} remaining")
                    
                else:
                    # Free downloads exhausted - Show beautiful subscribe card
                    st.warning("⚠️ You've used your 2 free downloads!")
                    
                    # Beautiful Subscribe Card
                    st.markdown("""
                    <div style="
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px 0 30px 0;">
                        
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 20px;
                            padding: 3px;
                            max-width: 500px;
                            width: 100%;
                            box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                            
                            <div style="
                                background: white;
                                border-radius: 18px;
                                padding: 40px 30px;
                                text-align: center;">
                                
                                <!-- Popular Badge -->
                                <span style="
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    padding: 8px 20px;
                                    border-radius: 30px;
                                    font-size: 14px;
                                    font-weight: 600;
                                    letter-spacing: 1px;
                                    text-transform: uppercase;
                                    margin-bottom: 20px;
                                    display: inline-block;">
                                    ⭐ MOST POPULAR
                                </span>
                                
                                <!-- Title -->
                                <h1 style="
                                    color: #333;
                                    font-size: 32px;
                                    margin: 20px 0 10px 0;
                                    font-weight: 700;">
                                    Unlimited Access
                                </h1>
                                
                                <!-- Price -->
                                <div style="
                                    margin: 20px 0;
                                    display: flex;
                                    align-items: baseline;
                                    justify-content: center;">
                                    <span style="
                                        font-size: 48px;
                                        font-weight: 800;
                                        color: #333;
                                        line-height: 1;">
                                        $9
                                    </span>
                                    <span style="
                                        font-size: 18px;
                                        color: #666;
                                        margin-left: 5px;">
                                        /month
                                    </span>
                                </div>
                                
                                <!-- Features List -->
                                <div style="
                                    text-align: left;
                                    margin: 30px 0;
                                    padding: 0 10px;">
                                    
                                    <div style="
                                        display: flex;
                                        align-items: center;
                                        margin: 15px 0;">
                                        <span style="
                                            background: #48bb78;
                                            color: white;
                                            width: 24px;
                                            height: 24px;
                                            border-radius: 50%;
                                            display: inline-flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 14px;
                                            margin-right: 12px;">
                                            ✓
                                        </span>
                                        <span style="
                                            color: #333;
                                            font-size: 16px;">
                                            <strong>Unlimited file downloads</strong>
                                        </span>
                                    </div>
                                    
                                    <div style="
                                        display: flex;
                                        align-items: center;
                                        margin: 15px 0;">
                                        <span style="
                                            background: #48bb78;
                                            color: white;
                                            width: 24px;
                                            height: 24px;
                                            border-radius: 50%;
                                            display: inline-flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 14px;
                                            margin-right: 12px;">
                                            ✓
                                        </span>
                                        <span style="
                                            color: #333;
                                            font-size: 16px;">
                                            <strong>All export formats</strong> (CSV, Excel, JSON)
                                        </span>
                                    </div>
                                    
                                    <div style="
                                        display: flex;
                                        align-items: center;
                                        margin: 15px 0;">
                                        <span style="
                                            background: #48bb78;
                                            color: white;
                                            width: 24px;
                                            height: 24px;
                                            border-radius: 50%;
                                            display: inline-flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 14px;
                                            margin-right: 12px;">
                                            ✓
                                        </span>
                                        <span style="
                                            color: #333;
                                            font-size: 16px;">
                                            <strong>Priority processing</strong>
                                        </span>
                                    </div>
                                    
                                    <div style="
                                        display: flex;
                                        align-items: center;
                                        margin: 15px 0;">
                                        <span style="
                                            background: #48bb78;
                                            color: white;
                                            width: 24px;
                                            height: 24px;
                                            border-radius: 50%;
                                            display: inline-flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 14px;
                                            margin-right: 12px;">
                                            ✓
                                        </span>
                                        <span style="
                                            color: #333;
                                            font-size: 16px;">
                                            <strong>Email support</strong>
                                        </span>
                                    </div>
                                </div>
                                
                                <!-- Subscribe Button -->
                                <a href="YOUR_GUMROAD_LINK" target="_blank">
                                    <button style="
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        border: none;
                                        padding: 16px 40px;
                                        border-radius: 50px;
                                        font-size: 20px;
                                        font-weight: 700;
                                        cursor: pointer;
                                        width: 100%;
                                        transition: transform 0.2s, box-shadow 0.2s;
                                        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);">
                                        👉 Subscribe Now
                                    </button>
                                </a>
                                
                                <!-- Guarantee -->
                                <p style="
                                    color: #999;
                                    font-size: 14px;
                                    margin-top: 20px;">
                                    🔒 Cancel anytime • Instant access • 30-day money-back guarantee
                                </p>
                                
                                <!-- Payment Icons -->
                                <div style="
                                    margin-top: 25px;
                                    display: flex;
                                    justify-content: center;
                                    gap: 15px;
                                    opacity: 0.6;">
                                    <span style="font-size: 24px;">💳</span>
                                    <span style="font-size: 24px;">📱</span>
                                    <span style="font-size: 24px;">🔒</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Call to action text -->
                    <p style="
                        text-align: center;
                        color: #666;
                        font-size: 16px;
                        margin: 10px 0 30px 0;
                        font-style: italic;">
                        👆 Subscribe above to unlock this file and unlimited access!
                    </p>
                    """, unsafe_allow_html=True)

                    # Still show the data preview
                    st.info("Preview your cleaned data below:")
                    st.dataframe(cleaned_df.head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please make sure your file is a valid CSV or Excel file")

else:
    # Show placeholder when no file uploaded
    with col2:
        st.subheader("🎯 See It In Action")
        
        # Create a sample messy DataFrame
        sample_data = pd.DataFrame({
            'Name ': ['John', 'Mary', '  Bob  ', 'John', None],
            'AGE  ': [25, None, 30, 25, 35],
            'Email   ': ['john@email.com', 'mary@email.com', None, 'john@email.com', 'bob@email.com'],
            'Join Date': ['2023-01-01', '01/15/2023', '2023-02-01', '2023-01-01', 'March 3, 2023']
        })
        
        st.markdown("**Example of what we fix:**")
        st.dataframe(sample_data, use_container_width=True)
        
        st.markdown("""
        **Common fixes we apply:**
        - 🧹 **Empty rows** automatically removed
        - 📝 **Column names** become clean (lowercase, no spaces)
        - 🔄 **Duplicates** identified and removed
        - 📅 **Dates** standardized to YYYY-MM-DD
        - ❓ **Missing values** handled intelligently
        
        **Perfect for:**
        - 📧 Marketing teams cleaning email lists
        - 💰 Accountants processing exports
        - 🔬 Researchers preparing datasets
        - 💼 Anyone tired of manual Excel work!
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <p>Made with ❤️ for data cleaners everywhere</p>
    <p style='font-size: 0.8em'>© 2024 CSV Cleaner Pro. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)