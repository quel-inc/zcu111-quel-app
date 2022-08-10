#include <stdio.h>
#include <stdlib.h>
#include "xrfdc.h"
#include "rfdc_interface.h"
#include "data_interface.h"
#include "clock_interface.h"
#include "rfdc_functions.h"
#define RFDC_DEVICE_ID  0

void clean_stdin(void)
{
	int c;
	do {
		c = getchar();
	} while (c != '\n' && c != EOF);
}

int main()
{
	int ret;
	char ch;
	unsigned int lmk_offset, lmx_offset;
	int tile_id, block_id, block_id2, tile_id2, block_id3, block_id4;
	int num, i;
	char action;
	int channel;
   	char filename[128];


	/* initialize RFDC instent*/
	ret = rfdc_inst_init(RFDC_DEVICE_ID);
	if(ret != XRFDC_SUCCESS) {
		printf("Failed to initilize RFDC\n");
		return -1;
	}

	/* configure LMX and LMK clock */
	ret = initRFclock(ZCU111, LMK04208_12M8_3072M_122M88_REVAB, DAC_245_76_MHZ, DAC_245_76_MHZ, ADC_245_76_MHZ);

	if(ret != SUCCESS){
		printf("Unable to configure RF clocks\n");
		return ret;
	}

	ret = init_mem();
	if(ret) {
		return FAIL;
	}

	/* initialise the gpio's for data path */
	ret = init_gpio();
	if(ret) {
		printf("Unable to initialise gpio's\n");
		goto err;
	}

start:
	printf("r: read, w: write, x: Exit\nPlease choose the action:");
	scanf("%c", &action);

    if (action==114 || action== 82){ //r or R		
		printf("Please choose the waveform file to write to:");
    	scanf("%s",filename);

		printf("Please enter ADC tile ID:");
		scanf("%d", &tile_id);

		printf("Please enter ADC block ID:");
		scanf("%d", &block_id);

		clean_stdin();

		if((tile_id >= ADC_MAX_TILE) || (block_id >= ADC_MAX_BLOCK)) {
			printf("Invalid pair of Tile ID and Block ID entered\n");
			goto err;
		}

		int lines;
		printf("Please choose the number of samples:");
		scanf("%d", &lines);

		signed short *wave;
		wave = (signed short *)malloc(lines * (sizeof(signed short)));

		ret = ReadDataFromMemory(wave, tile_id, block_id, lines * sizeof(signed short),0);

		FILE *fb = NULL;

		fb = fopen(filename,"a");
		
		for(i = 0; i<lines; i++){
			num = wave[i];
			fprintf(fb, "%d\n",num);
		}

		fclose(fb);
		free(wave);

		printf("Wave was succesfully read from tile: %d, block: %d with %d samples and written to file %s\n", tile_id, block_id, lines, filename);

		goto start;

    }

    else if (action==119 || action== 87){ //w or W
		printf("Please choose the waveform file to read from:");
    	scanf("%s",filename);

		/* Open waveform */
		int lines;
		lines = 0;

		FILE *f;
		f = fopen(filename,"r");

		if (f == NULL){
			printf("File open error\n");
			exit(1);
		}

		int reading;
		reading = 1;

		char getchar[20];

		while (reading ==1){
			if ((fscanf(f,"%s",&getchar[0])) == EOF){
				reading = 0;
				lines -= 1;
				}
			lines += 1;
		}
		fclose(f);

		f = fopen(filename,"r");
		signed short *wave;
		wave = (signed short *)malloc(lines * (sizeof(signed short)));
		
		for (i = 0; i<lines; i++){
			fscanf(f,"%d", &num);
			wave[i] = num;}
		fclose(f);

		again:
		printf("Please choose the number of channels to write:");
		scanf("%d", &channel);
		switch(channel){
			case 1:	
				printf("Please enter DAC tile ID:");
				scanf("%d", &tile_id);
				printf("Please enter DAC block ID:");
				scanf("%d", &block_id);			
				clean_stdin();
				if((tile_id >= DAC_MAX_TILE) || (block_id >= DAC_MAX_BLOCK)) {
					printf("Invalid pair of Tile ID and Block ID entered\n");
					goto err;
				}
				
				ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
				if(ret != 0) {
					printf("Failed to write data to DAC. Error: %d\n", ret);
					goto err;
				}
				free(wave);
				printf("static wave was generated according to the file %s, of %d samples, on tile: %d, block %d\n", filename, lines, tile_id, block_id);
				goto start;		
			case 2:
				printf("Please enter DAC tile ID:");
				scanf("%d", &tile_id);
				printf("Please enter the first DAC block ID:");
				scanf("%d", &block_id);
				printf("Please enter the second DAC block ID:");
				scanf("%d", &block_id2);
				clean_stdin();
				if((tile_id >= DAC_MAX_TILE) || (block_id >= DAC_MAX_BLOCK)) {
					printf("Invalid pair of Tile ID and Block ID entered\n");
					goto err;
				}
				if((tile_id >= DAC_MAX_TILE) || (block_id2 >= DAC_MAX_BLOCK)) {
					printf("Invalid pair of Tile ID and Block ID entered\n");
					goto err;
				}

				ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
				if(ret != 0) {
					printf("Failed to write data to DAC. Error: %d\n", ret);
					goto err;
				}
				ret = WriteDataToMemory(wave, tile_id, block_id2, lines * sizeof(signed short));
				if(ret != 0) {
					printf("Failed to write data to DAC. Error: %d\n", ret);
					goto err;
				}
				free(wave);
				printf("static wave was generated according to the file %s, of %d samples, on tile: %d, block %d and block %d\n", filename, lines, tile_id, block_id, block_id2);
				goto start;
			case 3:		
				printf("Please enter the first DAC tile ID:");
				scanf("%d", &tile_id);
				printf("Please enter the second DAC tile ID:");
				scanf("%d", &tile_id2);
				if (tile_id == tile_id2){
					printf("Please enter the first DAC block ID:");
					scanf("%d", &block_id);
					printf("Please enter the second DAC block ID:");
					scanf("%d", &block_id2);
					printf("Please enter the third DAC block ID:");
					scanf("%d", &block_id3);
					clean_stdin();
					if((tile_id >= DAC_MAX_TILE) || (block_id >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					if((tile_id >= DAC_MAX_TILE) || (block_id2 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					if((tile_id >= DAC_MAX_TILE) || (block_id2 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}

					ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id, block_id2, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id, block_id3, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					free(wave);
					printf("static wave was generated according to the file %s, of %d samples, on tile: %d, blocks %d, %d and %d.\n", 
					filename, lines, tile_id, block_id, block_id2, block_id3);
					goto start;
				}
				else {
					printf("For Tile ID %d:\n", tile_id);
					printf("Please enter the first DAC block ID:");
					scanf("%d", &block_id);
					printf("Please enter the second DAC block ID:");
					scanf("%d", &block_id2);
					clean_stdin();
					if((tile_id >= DAC_MAX_TILE) || (block_id >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					if((tile_id >= DAC_MAX_TILE) || (block_id2 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}

					printf("For Tile ID %d:\n", tile_id2);
					printf("Please enter DAC block ID:");
					scanf("%d", &block_id3);
					clean_stdin();
					if((tile_id >= DAC_MAX_TILE) || (block_id3 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id, block_id2, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id2, block_id3, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					free(wave);
					printf("static wave was generated according to the file %s, of %d samples, on tile: %d, block %d and block %d\n As well on the tile: %d, block %d.", 
					filename, lines, tile_id, block_id, block_id2, tile_id2, block_id3);
					goto start;
				}
			case 4:
				printf("Please enter the first DAC tile ID:");
				scanf("%d", &tile_id);
				printf("Please enter the second DAC tile ID:");
				scanf("%d", &tile_id2);
				if (tile_id == tile_id2){
					for (block_id=0; block_id<4; block_id++){
						ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
						if(ret != 0) {
							printf("Failed to write data to DAC. Error: %d\n", ret);
							goto err;
						}
					}
						free(wave);
					printf("static wave was generated according to the file %s, of %d samples, on all blocks of tile %d", filename, lines, tile_id);
					goto start;
				}
				else {
					printf("For Tile ID %d:\n", tile_id);
					printf("Please enter the first DAC block ID:");
					scanf("%d", &block_id);
					printf("Please enter the second DAC block ID:");
					scanf("%d", &block_id2);
					clean_stdin();
					if((tile_id >= DAC_MAX_TILE) || (block_id >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					if((tile_id >= DAC_MAX_TILE) || (block_id2 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}

					printf("For Tile ID %d:\n", tile_id2);
					printf("Please enter the first DAC block ID:");
					scanf("%d", &block_id3);
					printf("Please enter the second DAC block ID:");
					scanf("%d", &block_id4);
					clean_stdin();
					if((tile_id >= DAC_MAX_TILE) || (block_id3 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					if((tile_id >= DAC_MAX_TILE) || (block_id4 >= DAC_MAX_BLOCK)) {
						printf("Invalid pair of Tile ID and Block ID entered\n");
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id, block_id2, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id2, block_id3, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					ret = WriteDataToMemory(wave, tile_id2, block_id4, lines * sizeof(signed short));
					if(ret != 0) {
						printf("Failed to write data to DAC. Error: %d\n", ret);
						goto err;
					}
					free(wave);
					printf("static wave was generated according to the file %s, of %d samples, on tile: %d, block %d and block %d\n As well on the tile: %d, block %d and %d.", 
					filename, lines, tile_id, block_id, block_id2, tile_id2, block_id3, block_id4);
					goto start;
				}
			case 8:
				for (tile_id=0; tile_id<2; tile_id++){
					for (block_id=0; block_id<4; block_id++){
						ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
						if(ret != 0) {
							printf("Failed to write data to DAC. Error: %d\n", ret);
							goto err;
						}
					}
				}
				free(wave);
				printf("static wave was generated according to the file %s, of %d samples, on all tiles and blocks", filename, lines);
				goto start;
			default:
				printf("Please choose a number between 1,2,3,4,8.\n");
				goto again;
		}
	}


    else if (action==120 || action== 88){ //x or X
        goto err;
    }

    else {
        goto start;
    }

err:
	ret = disable_mem();
	if(ret != SUCCESS) {
		printf("Failed to disable data path. Error: %d\n", ret);
	}
	return FAIL;
}

