import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from PIL import Image
if __name__ == '__main__':
    rcParams['font.family'] = 'serif'  # Choose a font family (e.g., sans-serif, serif, monospace)

    path = r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\runs\DDPM_conditional_pokemon\csv.csv"
    img_10 = Image.open(r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\postprocessing\pokemon_epoch26.png")
    img_100 = Image.open(r"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\postprocessing\pokemon_epoch100.png")
    df = pd.read_csv(path)[:-5]
    fig, ax = plt.subplots(1)
    fig.suptitle("Conditional DDPM on Pokémon")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE")
    ax.plot(df["Value"], c="black", alpha=0.3, linewidth=1)
    ax.plot(df["Value"][200:300], c="g", alpha=1, linewidth=1.1)
    ax.plot(df["Value"][-100:], c='slateblue', alpha=1, linewidth=1.1)
    ax.set_xticks([i for i in range(0, len(df["Value"])+1, len(df["Value"]) // 10)], [i // 10 for i in range(0, len(df["Value"])+1, len(df["Value"]) // 10)])

    # Create an inset axes
    ax_ins_10 = inset_axes(ax, width="60%", height="55%", loc='upper left')
    ax_ins_100 = inset_axes(ax, width="60%", height="55%", loc='center right')

    # Plot the zoomed-in data
    n = 100

    ax_ins_10.imshow(img_10)
    ax_ins_100.imshow(img_100)

    # Set labels and title for the inset plot
    title_bbox_props = dict(boxstyle='round', facecolor='green', edgecolor='none', alpha=0.9)
    ax_ins_10.set_title("Epoch 30", color='black', bbox=title_bbox_props)

    ax_ins_10.set_xticks([], [])
    ax_ins_100.set_xticks([], [])
    ax_ins_10.set_yticks([], [])
    ax_ins_100.set_yticks([], [])
    # ax_ins_10.set_xticks([i+img_10.size[0]/2 for i in range(0, img_10.size[0]*6, img_10.size[0])], ["Airplane", "Car", "Bird", "Cat", "Deer", "Dog"])
    title_bbox_props = dict(boxstyle='round', facecolor='slateblue', edgecolor='none', alpha=0.9)
    ax_ins_100.set_title("Epoch 100", color='black', bbox=title_bbox_props)

    # ax_ins_100.set_xticks([i+img_100.size[0]/2 for i in range(0, img_100.size[0]*6, img_100.size[0])], ["Airplane", "Car", "Bird", "Cat", "Deer", "Dog"])

    # fig.tight_layout()
    # Add a rectangle patch to highlight the zoomed-in region in the main plot
    # Add a rectangle patch to highlight the last 1000 values in the main plot
    rect_10= plt.Rectangle((len(df) - n, min(df['Value'][-n:])), n, max(df['Value'][-n:]) - min(df['Value'][-n:]),
                         linewidth=2, edgecolor='slateblue', facecolor='none')
    rect_100 = plt.Rectangle((200, min(df['Value'][200:300])), 100, max(df['Value'][200:300]) - min(df['Value'][200:300]),
                         linewidth=2, edgecolor='g', facecolor='none')
    ax.add_patch(rect_10)
    ax.add_patch(rect_100)


    # Display the legend for both plots

    plt.show()