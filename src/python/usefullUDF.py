

def merging_data_frame(left_data_frame: pd.DataFrame, right_data_frame: pd.DataFrame, join_type: str, left_keys: str,
                       right_keys: str) -> pd.DataFrame:
    if left_keys != right_keys:
        if left_data_frame[left_keys].dtype != 'int64':
            left_data_frame[left_keys + '_lower'] = left_data_frame[left_keys].str.lower()
            right_data_frame[right_keys + '_lower'] = right_data_frame[right_keys].str.lower()
        else:
            left_data_frame[left_keys + '_lower'] = left_data_frame[left_keys]
            right_data_frame[right_keys + '_lower'] = right_data_frame[right_keys]

        _temp = pd.merge(left=left_data_frame, right=right_data_frame, how=join_type, on=None,
                         left_on=left_keys + '_lower', right_on=right_keys + '_lower',
                         left_index=False, right_index=False, sort=True, suffixes=('_x', '_y'), copy=True,
                         indicator=False, validate=None)
        output_df = _temp.drop([left_keys + '_lower', right_keys + '_lower', right_keys], axis=1)
    else:
        output_df = pd.merge(left=left_data_frame, right=right_data_frame, how=join_type, on=left_keys,
                             left_index=False, right_index=False, sort=True, suffixes=('_x', '_y'), copy=True,
                             indicator=False, validate=None)

    return output_df

def read_csv_file(input_path: str, file_name: str, encoding_type: str, delimiter_type: str) -> pd.DataFrame:
    lg.info("--- [INFO]: Importing " + file_name + " File.")
    try:
        output = pd.read_csv(input_path + file_name + '.csv', encoding=encoding_type, engine='python', delimiter=delimiter_type)
        lg.info("--- [INFO]: Importing Complete for " + file_name + " File.")
        return output
    except:
        lg.info("--- [INFO]: Importing Failed for " + file_name + " File.")
    return None


def reading_config(config_file_path: str, file_name: str, orient_type: str, typ_type: str) -> str:
    try:
        config_file = json.loads(pd.read_json(config_file_path + '/'+file_name+'.json', orient=orient_type,typ=typ_type).to_json())
        lg.info("--- [INFO]: Reading Configuration File Completed")
        return config_file
    except ImportError:
        lg.error("--- [ERROR]: Reading Configuration File Failed")

def write_to_csv(out_path: str, data_export: pd.DataFrame, file_name: str, extn_of_file: str, time_stamp_flag: bool, index_flag: bool, encoding_type: str) -> None:
    if time_stamp_flag:
        data_export.to_csv(
            out_path + '/' + file_name + '_' + datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.' + extn_of_file, index=index_flag, encoding=encoding_type)
    else:
        data_export.to_csv(out_path + '/' + file_name + '.' + extn_of_file, index=index_flag, encoding=encoding_type)
    lg.info("--- [INFO]: Export is completed for " + [x for x in globals() if globals()[x] is data_export][0])

def write_to_json(out_path: str, json_file_name: str, input_json: dict, ascii_flag: bool, indent_space: int,
                  encoding: str, time_stamp_flag: bool) -> None:
    if time_stamp_flag:
        with open(out_path + json_file_name + '_' + datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.json', 'w',
                  encoding=encoding) as f:
            json.dump(input_json, f, ensure_ascii=ascii_flag, indent=indent_space)
    else:
        with open(out_path + json_file_name + '.json', 'w', encoding=encoding) as f:
            json.dump(input_json, f, ensure_ascii=ascii_flag, indent=indent_space)
    lg.info("--- [INFO]: JSON export is completed.")
    
def date_formatting(input_df: pd.DataFrame, date_var_name: str, current_format: str) -> pd.DataFrame:
    # desired_format = '%d-%b-%Y'
    # current_format = '%m/%d/%Y'
    input_df[date_var_name+'_formatted'] = pd.to_datetime(input_df[date_var_name], format=current_format) #.dt.strftime(desired_format)
    input_df.drop([date_var_name], axis=1, inplace=True)
    input_df.rename(columns={date_var_name+'_formatted': date_var_name}, inplace=True)
    return input_df

def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist
