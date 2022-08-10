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

int main(int argc, char *argv[])
{
	int ret;
	char ch;
	unsigned int lmk_offset, lmx_offset;
	int tile_id, block_id;
	int num, i;

	/* initialize RFDC instent*/
	ret = rfdc_inst_init(RFDC_DEVICE_ID);
	if(ret != XRFDC_SUCCESS) {
		printf("Failed to initilize RFDC\n");
		return -1;
	}

	clean_stdin();

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

	printf("Please enter DAC tile ID:");
	scanf("%d", &tile_id);

	printf("Please enter DAC block ID:");
	scanf("%d", &block_id);

	clean_stdin();

	if((tile_id >= DAC_MAX_TILE) || (block_id >= DAC_MAX_BLOCK)) {
		printf("Invaild pair of Tile ID and Block ID entered\n");
		goto err;
	}

	/* Open waveform */
	int lines;

	FILE *f;
	f = fopen(argv[1],"r");

	if (f == NULL){
		printf("File open error\n");
		exit(1);
	}

	lines = 0;
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

	printf("Got number of samples: %d\n", lines);

	f = fopen(argv[1],"r");
	signed short *wave;
	wave = (signed short *)malloc(lines * (sizeof(signed short)));
	
	for (i = 0; i<lines; i++){
		fscanf(f,"%d", &num);
		wave[i] = num;
	}
	fclose(f);
	printf("wave file read\n");
	printf("Wave[0] = %d, Wave[%d] = %d, Wave[%d] = %d \n", wave[0], lines/2, wave[lines/2], lines, wave[lines-1]);
i
	/* write samples to RFDC using DMA */
	ret = WriteDataToMemory(wave, tile_id, block_id, lines * sizeof(signed short));
	free(wave);

	if(ret != 0) {
		printf("Failed to write data to DAC. Error: %d\n", ret);
		goto err;
	}

	printf("Static wave was generated according to the file %s, of %d samples, on tile: %d, block %d\n", argv[1], lines, tile_id, block_id);

here:
	printf("Press Enter to stop data samples and exit\n");
	ch = fgetc(stdin);

	if(ch == '\n') {
		/* stop DMA to sending data */
		ret = disable_mem();
		if(ret != SUCCESS) {
			printf("Failed to disable data path. Error: %d\n", ret);
		}
	} else {
		goto here;
	}

	return SUCCESS;

err:
	ret = disable_mem();
	if(ret != SUCCESS) {
		printf("Failed to disable data path. Error: %d\n", ret);
	}
	return FAIL;
}
