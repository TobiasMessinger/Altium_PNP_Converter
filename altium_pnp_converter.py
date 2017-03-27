import argparse
import sys
from colorama import init, Fore
import pandas as pd


def convert_pnp_file(file):
    sys.stdout.write("Reading Altium pick-n-place file {} ...\n\n".format(file))

    try:
        df = pd.read_csv(file,
                         names=['Designator', 'Comment', 'Layer', 'Footprint', 'Center_X', 'Center_Y',
                                'Rotation', 'Ref_X', 'Ref_Y', 'Pad_X', 'Pad_Y'],
                         skiprows=13,
                         dtype=object,
                         encoding='latin_1')
    except FileNotFoundError:
        sys.stderr.write(Fore.Red + "File {} not found".format(file))
        exit()

    # sort data frame alphabetically by designator
    df.sort_values(['Layer', 'Designator'], inplace=True)

    # change layer names to single character versions
    df.Layer = df.Layer.map({'TopLayer': 'T', 'BottomLayer': 'B'})

    # format X and Y coordinates
    df.Center_X = df.Center_X.apply(str.replace, args=[',', '.'])
    df.Center_Y = df.Center_Y.apply(str.replace, args=[',', '.'])
    df.Center_X = df.Center_X.apply(lambda x: x.upper().strip('MM'))
    df.Center_Y = df.Center_Y.apply(lambda x: x.upper().strip('MM'))
    df.Center_X = df.Center_X.apply(lambda x: "{:.2f}MM".format(float(x)))
    df.Center_Y = df.Center_Y.apply(lambda x: "{:.2f}MM".format(float(x)))

    # format rotation
    df.Rotation = df.Rotation.apply(lambda x: "{:.2f}".format(float(x)))

    return df


def save_pnp_data(df, file):
    sys.stdout.write("Saving output to  {}.txt\n\n".format(file))

    with open(file+'.txt', 'w') as f:
        for index, row in df.iterrows():
            f.write("{:16.16}{:16.16}{:16.16}{:8.8}{:8.8}{:40.40}{}\n".format(
                row['Designator'],
                row['Center_X'],
                row['Center_Y'],
                row['Rotation'],
                row['Layer'],
                row['Footprint'],
                row['Comment']))


def main():
    parser = argparse.ArgumentParser(prog=None,
                                     usage=None,
                                     description=None)
    parser.add_argument('input', help="Input file")
    parser.add_argument('-o', '--output', type=str, required=False, help="Output file")
    args = parser.parse_args()

    pnp = convert_pnp_file(args.input)

    if args.output:
        save_pnp_data(pnp, args.output)
    else:
        save_pnp_data(pnp, args.input.strip('.csv'))


if __name__ == '__main__':
    init()  # init for colorama / colorized text output
    main()
