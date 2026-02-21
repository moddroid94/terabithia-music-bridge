import React, { useState, useEffect } from 'react';
import { RunItem } from '../types';
import { Button, Input, Select, Textarea, Card } from './ui/Common';
import { Icons } from './ui/Icons';

interface ReportInfoProps {
    reportItem: RunItem;
    onCancel: () => void;
}

export const ReportInfo: React.FC<ReportInfoProps> = ({ reportItem, onCancel }) => {


    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-0 flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-200">
                <div className="flex items-center justify-between border-b border-gray-200 bg-gray-50 p-4 dark:border-zinc-800 dark:bg-zinc-900/50 sticky top-0 z-10 backdrop-blur-md">
                    <div className="text-gray-900 dark:text-white">
                        <span className="text-lg"><b>{reportItem.name}</b></span>
                        <br></br>
                        <span className="text-sm text-gray-400">Runned @ {reportItem.runnedAt.slice(0, 19)}</span>
                    </div>
                    <button onClick={onCancel} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                        <Icons.X size={20} />
                    </button>
                </div>
                <div className="flex items-center justify-between bg-gray-50 p-4 dark:bg-zinc-900/50 backdrop-blur-md">
                    <h2 className="text-lg text-gray-900 dark:text-white">
                        Tracklist:
                    </h2>
                </div>
                <div className="flex flex-col p-4 gap-5 justify-between overflow-auto">
                    {reportItem.tracklist.map((runitem, idx) => {
                        const time = Math.floor(runitem["LENGTH"])
                        const minutes = Math.floor(time / 60)
                        const secs = time - (minutes * 60)
                        return (
                            <div className="flex border-b border-zinc-800">
                                <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 mr-4 shrink-0">
                                    <img className="rounded-full" src={"data:image/png;base64," + runitem["ARTWORK"]}></img>
                                </div>
                                <div className="flex h-10 font-light items-center justify-between w-full mb-2">
                                    <div className=""><b>{runitem["title"]}</b> <div className="text-sm">{runitem["artist"]}</div></div>
                                    <div className="">{minutes}:{secs.toString().length < 2 ? "0" + secs : secs}</div>
                                </div>

                            </div>)
                    })}
                </div>

                <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-200 bg-gray-50 dark:border-zinc-800 dark:bg-zinc-900 sticky bottom-0 z-10">
                    <Button variant="ghost" onClick={onCancel}>Close</Button>
                </div>
            </Card>
        </div>
    );
};