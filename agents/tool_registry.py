from tools.process_tools import DataProcessingTools

TOOL_REGISTRY = {
    "DROP_COLUMNS": DataProcessingTools.drop_columns,
    "DROP_DUPLICATES": DataProcessingTools.remove_duplicates,

    "FILL_MISSING_MEAN": DataProcessingTools.fill_missing_mean,
    "FILL_MISSING_MEDIAN": DataProcessingTools.fill_missing_median,
    "FILL_MISSING_MODE": DataProcessingTools.fill_missing_mode,
    "DROP_MISSING": DataProcessingTools.drop_missing,

    "REMOVE_OUTLIERS": DataProcessingTools.remove_outliers_iqr,
    "CLIP_OUTLIERS": DataProcessingTools.clip_outliers,

    "ONE_HOT_ENCODING": DataProcessingTools.one_hot_encode,
    "TARGET_ENCODING": DataProcessingTools.target_encode,
    "FREQUENCY_ENCODING": DataProcessingTools.frequency_encode,

    "STANDARD_SCALER": DataProcessingTools.standard_scale,
    "MINMAX_SCALER": DataProcessingTools.minmax_scale,
    "ROBUST_SCALER": DataProcessingTools.robust_scale,

    "CONVERT_DATETIME": DataProcessingTools.convert_datetime,
    "EXTRACT_DATETIME_FEATURES": DataProcessingTools.extract_datetime_features,

    "CREATE_SHIPPING_DELAY": DataProcessingTools.create_shipping_delay,
    "CREATE_UNIT_PRICE": DataProcessingTools.create_unit_price,
    "CREATE_RATIO_FEATURE": DataProcessingTools.create_ratio_feature,
    "CREATE_DIFFERENCE_FEATURE": DataProcessingTools.create_difference_feature,
    "CREATE_INTERACTION_FEATURE": DataProcessingTools.create_interaction_feature,

    "LOG_TRANSFORM": DataProcessingTools.log_transform,
}