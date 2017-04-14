import argparse
import sys
from colorama import init, Fore
import pandas as pd


def convert_pnp_file(input_file, start_row, header, x_column, y_column):
    sys.stdout.write("Reading Altium pick-n-place file {} ...\n\n".format(input_file))

    try:
        df = pd.read_csv(input_file,
                         names=header,
                         skiprows=start_row-1,
                         sep=',',
                         dtype=object,
                         encoding='latin_1')
    except FileNotFoundError:
        sys.stderr.write("{}File {} not found".format(Fore.RED, input_file))
        exit()

    # sort data frame alphabetically by designator
    df.sort_values(['Layer', 'Designator'], inplace=True)

    # change layer names to single character versions
    df.Layer = df.Layer.map({'TopLayer': 'T', 'BottomLayer': 'B'})

    # format X and Y coordinates
    df[x_column] = df[x_column].apply(str.replace, args=[',', '.'])
    df[y_column] = df[y_column].apply(str.replace, args=[',', '.'])
    df[x_column] = df[x_column].apply(lambda x: x.upper().strip('MM'))
    df[y_column] = df[y_column].apply(lambda x: x.upper().strip('MM'))
    df[x_column] = df[x_column].apply(lambda x: "{:.2f}MM".format(float(x)))
    df[y_column] = df[y_column].apply(lambda x: "{:.2f}MM".format(float(x)))

    # format rotation
    df.Rotation = df.Rotation.apply(lambda x: "{:.2f}".format(float(x)))

    return df


def save_pnp_data(df, output_file, x_column, y_column):
    if not(output_file.endswith('.txt')):
        output_file = output_file + '.txt'

    sys.stdout.write("Saving output to {}\n\n".format(output_file))

    with open(output_file, 'w') as f:
        for index, row in df.iterrows():
            f.write("{:16.16}{:16.16}{:16.16}{:8.8}{:8.8}{:40.40}{}\n".format(
                row['Designator'],
                row[x_column],
                row[y_column],
                row['Rotation'],
                row['Layer'],
                row['Footprint'],
                row['Comment']))


if __name__ == '__main__':
    init()  # init for colorama / colorized text output

    parser = argparse.ArgumentParser(prog=None,
                                     usage=None,
                                     description=None)
    parser.add_argument('input', help="Input file")
    parser.add_argument('-o', '--output', type=str, required=False, help="Output file")
    parser.add_argument('-s', '--start_row', type=int, required=False, help="First row of PNP data")
    parser.add_argument('-x', '--x_column', type=str, required=False, help="Name of column containing x coordinates")
    parser.add_argument('-y', '--y_column', type=str, required=False, help="Name of column containing y coordinates")
    parser.add_argument('-c', '--csv_header', type=str, nargs='+', required=False, help="Input file column names")
    args = parser.parse_args()

    # default parameters
    h = ['Designator', 'Comment', 'Layer', 'Footprint', 'Center_X', 'Center_Y', 'Rotation', 'Ref_X', 'Ref_Y', 'Pad_X',
         'Pad_Y']
    x = 'Center_X'
    y = 'Center_Y'

    if args.header:
        print(args.header)
    else:
        print(h)

    pnp = convert_pnp_file(args.input, 14, h, x, y)

    if args.output:
        save_pnp_data(pnp, args.output, x, y)
    else:
        save_pnp_data(pnp, args.input.strip('.csv'), x, y)
